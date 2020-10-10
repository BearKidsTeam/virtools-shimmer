#pragma once
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#define DLLEXP __declspec(dllexport)
template<class dst, class src> dst union_cast(src s)
{
	union
	{
		dst d;
		src s;
	}conv;
	conv.s = s;
	return conv.d;
}
extern FARPROC GetCK2Func(LPCSTR funcname);
