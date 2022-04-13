#!/usr/bin/env bash

protoc --proto_path . --python_out=protopython --ruby_out=ruby proto/*
