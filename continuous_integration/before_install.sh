#!/usr/bin/env bash
ci_dir="$(dirname "${BASH_SOURCE[0]}")"
full_path_ci_dir="$(cd "${ci_dir}" && pwd)"
git_root="$(dirname "$full_path_ci_dir")"
container_id="kerberosauthenticator-testing"
docker run --rm -d \
    -h address.example.com \
    -p 88:88/udp \
    -p 8888:8888 \
    --name $container_id \
    -v "$git_root":/working \
    jcrist/kerberosauthenticator-testing 
