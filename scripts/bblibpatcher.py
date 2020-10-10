import sys
import os.path as path
import struct

common_patches = {
    b"CK2.dll": b"CKS.dll",
    b"?RGBAFTOCOLOR@@YAKMMMM@Z": b"?RGBAFTOCOLOR@@YAIMMMM@Z",
    b"?RGBAFTOCOLOR@@YAKPBUVxColor@@@Z": b"?RGBAFTOCOLOR@@YAIPBUVxColor@@@Z"
}

vtablemap = dict()
projroot = path.normpath(path.join(path.dirname(__file__), ".."))
datadir = path.normpath(path.join(projroot, "data"))

def load_vtable_mapping():
    with open(f"{datadir}/vtable.map", "r") as f:
        cls = ""
        for ll in f:
            l = ll.rstrip()
            if not l.startswith('\t') and l.endswith(':'):
                cls = l[:-1]
                if cls not in vtablemap:
                    vtablemap[cls] = dict()
            elif l.startswith('\t'):
                m = l.split(',')
                if len(m) < 2 or cls not in vtablemap:
                    continue
                vtablemap[cls][int(m[0], 16)] = int(m[1], 16)

def patch_vcalls(d, module):
    with open(f"{datadir}/{module}.vcalltype", "r") as f:
        cls = ""
        for ll in f:
            l = ll.rstrip()
            if not l.startswith('\t') and l.endswith(':'):
                cls = l[:-1]
                if cls not in vtablemap:
                    print(f"W: class {cls} has no vtable mapping defined.")
            elif l.startswith('\t'):
                for ofst in l.split(','):
                    offset = int(ofst, 16)
                    vcall, = struct.unpack("<I", d[offset:offset + 4])
                    if vcall not in vtablemap[cls]:
                        print(f"W: virtual function call {hex(offset)} is not mapped.")
                        continue
                    d[offset:offset + 4] = struct.pack("<I", vtablemap[cls][vcall])
    return d

if __name__=="__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <BBlibdll>")
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        d = bytearray(f.read())
        for i in common_patches:
            d = d.replace(i, common_patches[i])
        load_vtable_mapping()
        d = patch_vcalls(d, path.basename(sys.argv[1])[:-4])
        with open(f"{sys.argv[1][:-4]}.patched.dll", "wb") as outf:
            outf.write(d)

