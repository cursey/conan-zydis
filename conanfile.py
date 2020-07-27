from conans import ConanFile, CMake, tools
from textwrap import dedent


class ZydisConan(ConanFile):
    name = "zydis"
    version = "3.1.0"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Zydis here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "decoder": [True, False], "formatter": [
        True, False], "avx512": [True, False], "knc": [True, False]}
    default_options = {"shared": False, "decoder": True,
                       "formatter": False, "avx512": False, "knc": False}
    generators = "cmake"

    def source(self):
        self.run("git clone --recursive git@github.com:zyantific/zydis.git")
        self.run("cd zydis && git checkout v3.1.0")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("zydis/CMakeLists.txt", "project(Zydis VERSION 3.1.0.0 LANGUAGES C CXX)",
                              dedent("""project(Zydis VERSION 3.1.0.0 LANGUAGES C CXX)
                                        include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                                        conan_basic_setup()"""))

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ZYDIS_BUILD_SHARED_LIB"] = self.options.shared
        cmake.definitions["ZYDIS_FEATURE_DECODER"] = self.options.decoder
        cmake.definitions["ZYDIS_FEATURE_FORMATTER"] = self.options.formatter
        cmake.definitions["ZYDIS_FEATURE_AVX512"] = self.options.avx512
        cmake.definitions["ZYDIS_FEATURE_KNC"] = self.options.knc
        cmake.definitions["ZYDIS_BUILD_EXAMPLES"] = False
        cmake.definitions["ZYDIS_BUILD_TOOLS"] = False
        cmake.configure(source_folder="zydis")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="zydis/include")

        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", dst="include", src="zydis/msvc")

        self.copy("*.h", dst="include",
                  src="zydis/dependencies/zycore/include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Zydis"]

        if not self.options.shared:
            self.cpp_info.defines.append("ZYDIS_STATIC_DEFINE")
            self.cpp_info.defines.append("ZYCORE_STATIC_DEFINE")

        if not self.options.decoder:
            self.cpp_info.defines.append("ZYDIS_DISABLE_DECODER")

        if not self.options.formatter:
            self.cpp_info.defines.append("ZYDIS_DISABLE_FORMATTER")

        if not self.options.avx512:
            self.cpp_info.defines.append("ZYDIS_DISABLE_AVX512")

        if not self.options.knc:
            self.cpp_info.defines.append("ZYDIS_DISABLE_KNC")
