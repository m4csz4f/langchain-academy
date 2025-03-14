#!/bin/bash

# copy .env file from the root, to each of the modules

for i in {1..5}; do
  cp ./.env module-$i/studio/.env
done
cp ./.env module-0/.env