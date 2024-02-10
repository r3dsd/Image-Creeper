#pragma once

#include <iostream>
#include <vector>
#include <optional>
#include <tuple>
#include <filesystem>

namespace fs = std::filesystem;

class PngDescriptionManager {
public:

    PngDescriptionManager();
    std::vector<std::tuple<fs::path, std::string>> Load(const fs::path& folderpath);
    std::string GetPngRawData(const fs::path& filepath);
    static std::optional<std::string> GetPngDescription(const fs::path& filepath);
    static unsigned int ConvertEndian(unsigned int value);
private:
    static bool is_LittleEndian;
    void CheckEndianess();
};