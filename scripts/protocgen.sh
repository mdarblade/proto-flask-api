#!/usr/bin/env bash

protoc --proto_path . -I $(find proto -iname "*.proto") --python_out=py --ruby_out=ruby
