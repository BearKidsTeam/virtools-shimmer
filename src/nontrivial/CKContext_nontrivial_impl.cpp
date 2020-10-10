#include "CKContextShim.h"
long CKContext::OutputToConsoleEx(char* s, ...)
{
	typedef int (CKContext::*fp)(char*, int);
	static fp f = union_cast<fp>(GetCK2Func("?OutputToConsole@CKContext@@QAEHPADH@Z"));
	char *buf = new char[4096];
	va_list vl;
	va_start(vl, s);
	vsnprintf(buf, 4096, s, vl);
	va_end(vl);
	int ret = (this->*f)(buf, 0);
	delete buf;
	return ret;
}

long CKContext::OutputToConsoleExBeep(char* s, ...)
{
	typedef int (CKContext::*fp)(char*, int);
	static fp f = union_cast<fp>(GetCK2Func("?OutputToConsole@CKContext@@QAEHPADH@Z"));
	char *buf = new char[4096];
	va_list vl;
	va_start(vl, s);
	vsnprintf(buf, 4096, s, vl);
	va_end(vl);
	int ret = (this->*f)(buf, 1);
	delete buf;
	return ret;
}

char* CKContext::GetStringBuffer(int sz)
{
	static char *buf = nullptr;
	static int bsz = -1;

	if (bsz == -1)
	{
		bsz = sz;
		buf = new char[bsz];
	}
	else
	{
		if (bsz < sz)
		{
			delete[] buf;
			bsz = sz;
			buf = new char[bsz];
		}
	}
	return buf;
}
