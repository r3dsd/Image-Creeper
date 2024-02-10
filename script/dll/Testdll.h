#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

class Test {
public:
	int add (int a, int b);
	int sub (int a, int b);
};