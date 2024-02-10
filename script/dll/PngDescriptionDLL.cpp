#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl/filesystem.h>

#include "PngDescriptionManager.h"

namespace py = pybind11;

PYBIND11_MODULE(PngDescriptionDLL, m) {
	py::class_<PngDescriptionManager>(m, "PngDescriptionManager")
		.def(py::init<>())
		.def("Load", &PngDescriptionManager::Load)
		.def("GetPngDescription", &PngDescriptionManager::GetPngDescription)
		.def("GetPngRawData", &PngDescriptionManager::GetPngRawData);
}