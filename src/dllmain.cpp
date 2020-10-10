#include "common.h"

HMODULE ck2 = nullptr;

FARPROC GetCK2Func(LPCSTR funcname)
{
	if (ck2)
		return GetProcAddress(ck2, funcname);
	ck2 = LoadLibraryW(L"CK2.dll");
	return GetProcAddress(ck2, funcname);
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
		case DLL_PROCESS_ATTACH:
		case DLL_THREAD_ATTACH:
		case DLL_THREAD_DETACH:
		case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}
