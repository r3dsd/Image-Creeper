#include "PngDescriptionManager.h"
#include <fstream>
#include <array>
#include <sstream>
#include <future>
PngDescriptionManager::PngDescriptionManager() {
	PngDescriptionManager::CheckEndianess();
}

std::optional<std::string> PngDescriptionManager::GetPngDescription(const fs::path& filepath) {
    fs::path path = filepath;
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    std::array<char, 8> signature;
    file.read(signature.data(), signature.size());
    if (!file.good() || memcmp(signature.data(), "\x89PNG\r\n\x1a\n", 8) != 0) {
        throw std::runtime_error("Not a valid PNG file");
    }

    while (file.good()) {
        unsigned int chunkLength;
        if (!file.read(reinterpret_cast<char*>(&chunkLength), 4)) {
            throw std::runtime_error("Error reading chunk length");
        }
        chunkLength = PngDescriptionManager::ConvertEndian(chunkLength);
        char chunkType[5];
        file.read(chunkType, 4);
        chunkType[4] = '\0';

        if (strcmp(chunkType, "IDAT") == 0) {
            return std::nullopt;
        }

        if (strcmp(chunkType, "tEXt") == 0) {
            std::string keyValuePair;
            keyValuePair.resize(chunkLength);
            file.read(&keyValuePair[0], chunkLength);

            size_t separatorPos = keyValuePair.find('\0');
            if (separatorPos != std::string::npos) {
                std::string key = keyValuePair.substr(0, separatorPos);
                std::string value = keyValuePair.substr(separatorPos + 1);
                if (key == "Description") {
                    return value;
                }
            }
        }
        else {
            file.ignore(chunkLength);
        }

        file.ignore(4); // Skip CRC
    }

    return std::nullopt;
}

std::vector<std::tuple<fs::path, std::string>> PngDescriptionManager::Load(const fs::path& folderpath) {
    fs::path path = folderpath;
    std::vector<std::future<std::optional<std::tuple<fs::path, std::string>>>> futures;
    std::vector<std::tuple<fs::path, std::string>> result;

    const size_t max_concurrent_tasks = 4; // 동시에 실행할 최대 작업 수
    size_t current_tasks = 0;

    for (const auto& entry : fs::recursive_directory_iterator(path)) {
        if (entry.is_regular_file() && entry.path().extension() == ".png") {
            if (current_tasks >= max_concurrent_tasks) {
                // 현재 작업 수가 최대에 도달하면, 하나의 작업이 완료될 때까지 기다립니다.
                for (auto& fut : futures) {
                    if (fut.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                        auto opt = fut.get();
                        if (opt.has_value()) {
                            result.push_back(opt.value());
                        }
                        fut = {}; // 완료된 future를 제거합니다.
                        --current_tasks;
                        break; // 하나의 작업이 완료되었으므로 반복을 종료합니다.
                    }
                }
            }

            // 새 작업 추가
            futures.push_back(std::async(std::launch::async, &PngDescriptionManager::GetPngDescriptionAsync, this, entry.path()));
            ++current_tasks;
        }
    }

    // 남은 모든 futures 처리
    for (auto& fut : futures) {
        if (fut.valid()) { // 아직 처리되지 않은 future에 대해
            auto opt = fut.get();
            if (opt.has_value()) {
                result.push_back(opt.value());
            }
        }
    }

    return result;
}

std::string PngDescriptionManager::GetPngRawData(const fs::path& filepath) {
    fs::path path = filepath;

    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    std::array<char, 8> signature;
    file.read(signature.data(), signature.size());
    if (!file.good() || memcmp(signature.data(), "\x89PNG\r\n\x1a\n", 8) != 0) {
        throw std::runtime_error("Not a valid PNG file");
    }

    std::ostringstream result;
    while (file.good()) {
        unsigned int chunkLength;
        file.read(reinterpret_cast<char*>(&chunkLength), 4);
        chunkLength = _byteswap_ulong(chunkLength);

        char chunkType[5];
        file.read(chunkType, 4);
        chunkType[4] = '\0';

        result << chunkType << " " << chunkLength << " ";

        // Exclude image data (IDAT) chunks
        if (strcmp(chunkType, "IDAT") != 0) {
            if (chunkLength > 0) {
                std::vector<char> chunkData(chunkLength);
                file.read(chunkData.data(), chunkLength);
                std::string chunkContent(chunkData.begin(), chunkData.end());

                // Append a sanitized version of the chunk content to the result
                for (char c : chunkContent) {
                    if (isprint(static_cast<unsigned char>(c))) {
                        result << c;
                    }
                    else {
                        result << "\\x" << std::hex << std::setw(2) << std::setfill('0') << (static_cast<unsigned int>(c) & 0xff);
                    }
                }
            }
        }
        else {
            file.ignore(chunkLength); // Skip the image data
        }

        result << " ";

        file.ignore(4); // Skip CRC

        if (strcmp(chunkType, "IEND") == 0) {
            break;
        }
    }

    return result.str();
}

std::optional<std::string> PngDescriptionManager::GetPngDescription(const fs::path& filepath) {
    fs::path path = filepath;
    std::ifstream file(path, std::ios::binary);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    std::array<char, 8> signature;
    file.read(signature.data(), signature.size());
    if (!file.good() || memcmp(signature.data(), "\x89PNG\r\n\x1a\n", 8) != 0) {
        throw std::runtime_error("Not a valid PNG file");
    }

    while (file.good()) {
        unsigned int chunkLength;
        if (!file.read(reinterpret_cast<char*>(&chunkLength), 4)) {
            throw std::runtime_error("Error reading chunk length");
        }
        chunkLength = ConvertEndian(chunkLength);
        char chunkType[5];
        file.read(chunkType, 4);
        chunkType[4] = '\0';

        if (strcmp(chunkType, "IDAT") == 0) {
            return std::nullopt;
        }

        if (strcmp(chunkType, "tEXt") == 0) {
            std::string keyValuePair;
            keyValuePair.resize(chunkLength);
            file.read(&keyValuePair[0], chunkLength);

            size_t separatorPos = keyValuePair.find('\0');
            if (separatorPos != std::string::npos) {
                std::string key = keyValuePair.substr(0, separatorPos);
                std::string value = keyValuePair.substr(separatorPos + 1);
                if (key == "Description") {
                    return value;
                }
            }
        }
        else {
            file.ignore(chunkLength);
        }

        file.ignore(4); // Skip CRC
    }

    return std::nullopt;
}

void PngDescriptionManager::CheckEndianess() {
    unsigned int test = 1;
    char* testPtr = reinterpret_cast<char*>(&test);
    is_LittleEndian = (testPtr[0] == 1);
    std::cout << "System is " << (is_LittleEndian ? "little" : "big") << " endian" << std::endl;
}

unsigned int PngDescriptionManager::ConvertEndian(unsigned int value){
	if (is_LittleEndian) {
		return _byteswap_ulong(value);
	}
	return value;
}