from conans import ConanFile, CMake, tools


class ZydisConan(ConanFile):
    name = "zydis"
    version = "2.0.2"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Zydis here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        self.run("git clone --recursive git@github.com:zyantific/zydis.git")
        self.run("cd zydis && git checkout v2.0.2")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("zydis/CMakeLists.txt", "project(Zydis VERSION 2.0.2)",
                              '''project(Zydis VERSION 2.0.2)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
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

        self.copy("*.h", dst="include", src="zydis/dependencies/zycore/include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Zydis"]
        
        if not self.options.shared:
            self.cpp_info.defines.append("ZYDIS_STATIC_DEFINE")


