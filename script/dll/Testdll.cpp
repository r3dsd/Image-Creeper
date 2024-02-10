#include "Testdll.h"

int Test::add(int a, int b)
{
	return a + b;
}

int Test::sub(int a, int b)
{
	return a - b;
}

PYBIND11_MODULE(Testdll, m) {
	py::class_<Test>(m, "Test")
		.def(py::init<>())
		.def("add", &Test::add)
		.def("sub", &Test::sub);
}