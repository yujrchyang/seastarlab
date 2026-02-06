#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys

def run_cmd(cmd, cwd=None):
    print(f"--- Running: {' '.join(cmd)} in {cwd if cwd else os.getcwd()}")
    subprocess.check_call(cmd, cwd=cwd)

def main():
    parser = argparse.ArgumentParser(description="Configure SeastarLab")
    parser.add_argument('--mode', choices=['release', 'debug'], default='release', help='build mode')
    parser.add_argument('--submodule', action='store_true', default=False, help='download and build submodule')
    parser.add_argument('--config', action='store_true', default=False, help='config current project')
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    seastar_dir = os.path.join(root_dir, "thirdparty", "seastar")
    build_dir = os.path.join(root_dir, "build")

    if args.submodule:
        # 1. update submodule
        print("--- Initializing Submodule...")
        run_cmd(["git", "submodule", "update", "--init", "--recursive"])

        # 2. auto compile seastar
        seastar_build_dir = os.path.join(seastar_dir, "build", args.mode)
        if not os.path.exists(os.path.join(seastar_build_dir, "libseastar.a")):
            print("--- Compile Seastar...")
            run_cmd([
                sys.executable, "configure.py",
                "--mode=release",
                "--c++-standard=20",
                "--compile-commands-json"
            ], cwd=seastar_dir)
            run_cmd([
                "ninja",
                "-C",
                f"{seastar_build_dir}"
            ], cwd=seastar_dir)
        else:
            print("--- Seastar already builded")

    if args.config:
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        cmake_cmd = [
            "cmake",
            "-G", "Ninja",
            f"-DCMAKE_PREFIX_PATH={seastar_build_dir};{seastar_build_dir}/_cooking/installed",
            f"-DCMAKE_MODULE_PATH={seastar_dir}/cmake",
            root_dir
        ]
        run_cmd(cmake_cmd, cwd=build_dir)

        source_json = os.path.join(build_dir, "compile_commands.json")
        target_link = os.path.join(root_dir, "compile_commands.json")
        if os.path.exists(source_json):
            if os.path.lexists(target_link):
                os.remove(target_link)
            os.symlink(source_json, target_link)

        print(f"\n--- Configure finished. Now run: ninja -C {os.path.relpath(build_dir)}")

if __name__ == "__main__":
    main()
