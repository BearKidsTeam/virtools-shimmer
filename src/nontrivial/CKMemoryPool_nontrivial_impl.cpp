#include "CKMemoryPoolShim.h"
#include <VxAllocator.h>

CKMemoryPool::CKMemoryPool(CKContext*, int sz)
{
	s = new VxScratch(sz);
}

CKMemoryPool::~CKMemoryPool()
{
	delete s;
}

void *CKMemoryPool::Mem() const
{
	return s->Mem();
}
