// mathlib.c -- math primitives

#include "cmdlib.h"
#include "mathlib.h"

vec_t Q_rint(vec_t n)
{
	if (n >= 0)
		return (vec_t) ((int) (n + 0.5));
	else
		return (vec_t) ((int) (n - 0.5));
}

