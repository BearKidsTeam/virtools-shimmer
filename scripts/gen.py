import os
import sys
import json
import itertools
from string import ascii_lowercase
from pydemangle import demangle

funcdict = dict()
classes = dict()
projroot = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
datadir = os.path.normpath(os.path.join(projroot, "data"))
srcdir = os.path.normpath(os.path.join(projroot, "src"))
incl = '''//Auto generated file. Use patches to make necessary modifications.
#pragma once
#include "common.h"
#include <stdlib.h>
#include <XArray.h>
#include <XObjectArray.h>
#include <XSArray.h>
#include <XString.h>
#include <VxDefines.h>
#include <CKTypes.h>
#include <CKEnums.h>

'''

def load_imports():
    for impf in os.listdir(datadir):
        if impf.endswith(".imp"):
            with open(f"{datadir}/{impf}", "r") as f:
                for l in f:
                    export_func, call_func, non_trivial = tuple((l.strip() + (',' if l.count(',') == 1 else '')).split(','))
                    t = {"call_func": export_func if call_func == "trivial" else call_func, "non_trivial": non_trivial}
                    try:
                        if export_func in funcdict:
                            if t != funcdict[export_func]:
                                raise ValueError(f"conflicting export function {export_func}, file {impf}")
                        else:
                            funcdict[export_func] = t
                    except ValueError as e:
                        print(e)
                        print(f"note: new definition is {t}")
                        print(f"note: previous definition was {funcdict[export_func]}")
                        sys.exit(1)

def identifier_gen():
    for size in itertools.count(1):
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)

def strip_type(x):
    return x.replace("class ", "").replace("struct ", "").replace("enum ", "")

def decor_args(argslist, add_identifier):
    ret = list()
    if argslist == ["void"]:
        argslist.clear()
    for arg, identifier in zip(argslist, identifier_gen()):
        arg = strip_type(arg)
        if arg.find("...") != -1 and add_identifier:
            raise ValueError("cannot add identifier to a variadic function")
        if arg.find("(__cdecl *)") != -1:
            arg = arg.replace("(__cdecl *)", f"(*{identifier})", 1)
        elif add_identifier:
            arg += f" {identifier}"
        ret.append(arg)
    return ", ".join(ret)

def scan_classes():
    classes["_global"] = list()
    for f in funcdict:
        df = json.loads(demangle(f))
        if df["symbol_type"] == "class method":
            if df["class_name"] not in classes :
                classes[df["class_name"]] = list()
            o = dict()
            if "is_dtor" in df or "is_ctor" in df:
                o["is_dtor"] = "is_dtor" in df and df["is_dtor"]
                if (o["is_dtor"]):
                    o["virtual_dtor"] = df["function_signature"].startswith("public: virtual")
                o["is_ctor"] = "is_ctor" in df and df["is_ctor"]
            else:
                o["return_type"] = strip_type(df["return_type"])
            try:
                o["args_w_identifier"] = decor_args(df["args"], True)
            except ValueError:
                if funcdict[f]["non_trivial"] != 'N':
                    raise ValueError("variadic function can't have trivial implementation")
            o["args_wo_identifier"] = decor_args(df["args"], False)
            o["argc"] = 0 if df["args"] == ["void"] else len(df["args"])
            o["function_name"] = df["function_name"]
            o["sig"] = f
            classes[df["class_name"]].append(o)
        elif df["symbol_type"] == "global function":
            o = dict()
            o["return_type"] = strip_type(df["return_type"])
            o["args_w_identifier"] = decor_args(df["args"], True)
            o["args_wo_identifier"] = decor_args(df["args"], False)
            o["argc"] = 0 if df["args"] == ["void"] else len(df["args"])
            o["function_name"] = df["function_name"]
            o["sig"] = f
            classes["_global"].append(o)

def generate_global_header(f):
    f.write(incl)
    for func in sorted(classes["_global"], key=lambda x: x["sig"]):
        sys.stderr.write(f"\t{func['sig']}\n")
        f.write(f'DLLEXP {func["return_type"]} {func["function_name"]}({func["args_wo_identifier"]});\n')

def generate_class_header(cls, f):
    f.write(incl)
    f.write(
        f'class DLLEXP {cls}\n'
        '{\n'
        'public:\n'
        f'\t{cls} & operator=({cls} &&) = delete;\n'
        f'\t{cls} & operator=(const {cls} &) = delete;\n'
    )
    for func in sorted(classes[cls], key=lambda x: x["sig"]):
        sys.stderr.write(f"\t{func['sig']}\n")
        if "is_ctor" in func and func["is_ctor"]:
            f.write(f'\t{cls}({func["args_wo_identifier"]});\n')
        elif "is_dtor" in func and func["is_dtor"]:
            f.write(f'\t{"virtual " if func["virtual_dtor"] else ""}~{cls}({func["args_wo_identifier"]});\n')
        else:
            f.write(f'\t{func["return_type"]} {func["function_name"]}({func["args_wo_identifier"]});\n')
    f.write('};\n')

def generate_global_impl(f):
    f.write(f"//Auto generated trivial implementation of global functions\n")
    f.write(f'#include "GlobalShim.h"\n\n')
    
    for func in sorted(classes['_global'], key=lambda x: x["sig"]):
        if funcdict[func["sig"]]["non_trivial"]:
            continue
        f.write(f'{func["return_type"]} {func["function_name"]}({func["args_w_identifier"]})\n')
        f.write('{\n')
        f.write(f'\ttypedef {func["return_type"]} (*_fp)({func["args_wo_identifier"]});\n')
        f.write(f'\tstatic _fp F = union_cast<_fp>(GetCK2Func("{funcdict[func["sig"]]["call_func"]}"));\n')
        ag = identifier_gen()
        arglist = [next(ag) for i in range(func["argc"])]
        f.write(f'\treturn F({", ".join(arglist)});\n')
        f.write('}\n\n')

def generate_class_impl(cls, f):
    f.write(f"//Auto generated trivial implementation for {cls}\n")
    f.write(f'#include "{cls}Shim.h"\n\n')
    
    for func in sorted(classes[cls], key=lambda x: x["sig"]):
        if funcdict[func["sig"]]["non_trivial"]:
            continue
        no_return = False
        if "is_ctor" in func and func["is_ctor"]:
            f.write(f'{cls}::{cls}({func["args_w_identifier"]})\n')
            f.write('{\n')
            f.write(f'\ttypedef void ({cls}::*_fp)({func["args_wo_identifier"]});\n')
            no_return = True
        elif "is_dtor" in func and func["is_dtor"]:
            f.write(f'{cls}::~{cls}({func["args_wo_identifier"]})\n')
            f.write('{\n')
            f.write(f'\ttypedef void ({cls}::*_fp)({func["args_wo_identifier"]});\n')
            no_return = True
        else:
            f.write(f'{func["return_type"]} {cls}::{func["function_name"]}({func["args_w_identifier"]})\n')
            f.write('{\n')
            f.write(f'\ttypedef {func["return_type"]} ({cls}::*_fp)({func["args_wo_identifier"]});\n')
        f.write(f'\tstatic _fp F = union_cast<_fp>(GetCK2Func("{funcdict[func["sig"]]["call_func"]}"));\n')
        ag = identifier_gen()
        arglist = [next(ag) for i in range(func["argc"])]
        f.write(f'\t{"" if no_return else "return "}(this->*F)({", ".join(arglist)});\n')
        f.write('}\n\n')

if __name__ == "__main__":
    load_imports()
    scan_classes()
    for cls in classes:
        if cls == "_global":
            with open(f"{srcdir}/GlobalShim.h", "w") as f:
                sys.stderr.write("global:\n")
                generate_global_header(f)
            with open(f"{srcdir}/trivial/GlobalShim.cpp", "w") as f:
                generate_global_impl(f)
        else:
            with open(f"{srcdir}/{cls}Shim.h", "w") as f:
                sys.stderr.write(f"{cls}:\n")
                generate_class_header(cls, f)
            with open(f"{srcdir}/trivial/{cls}Shim.cpp", "w") as f:
                generate_class_impl(cls,f)
