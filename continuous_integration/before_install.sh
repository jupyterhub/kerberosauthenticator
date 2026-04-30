#!/usr/bin/env bash

set -eu

ci_dir="$(dirname "${BASH_SOURCE[0]}")"
full_path_ci_dir="$(cd "${ci_dir}" && pwd)"
git_root="$(dirname "$full_path_ci_dir")"
container_id="kerberosauthenticator-testing"
image_name=kerberosauthenticator-testing

docker build -t $image_name "$ci_dir/docker"

docker run --rm -d \
    -h address.example.com \
    -p 88:88/udp \
    -p 8888:8888 \
    --name $container_id \
    -v "$git_root":/working \
    $image_name
