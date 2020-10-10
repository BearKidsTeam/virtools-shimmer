#include "CKParameterManagerShim.h"
#include <cstdarg>

long CKParameterManager::RegisterNewStructure(CKGUID g, char * n, char * d, ...)
{
	typedef int (CKParameterManager::*_fp)(CKGUID, char*, char*, XArray<CKGUID>&);
	static _fp f = union_cast<_fp>(GetCK2Func("?RegisterNewStructure@CKParameterManager@@QAEHUCKGUID@@PAD1AAV?$XArray@UCKGUID@@@@@Z"));
	XArray<CKGUID> a;
	int cnt = *d ? 1 : 0;
	for (char *p = d; *p; ++p)
		if (*p == ',')
			++cnt;
	va_list args;
	va_start(args, d);
	for (int i = 0; i < cnt; ++i)
		a.PushBack(va_arg(args, CKGUID));
	va_end(args);
	return (this->*f)(g, n, d, a);
}
