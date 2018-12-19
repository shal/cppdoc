[license]: ./LICENSE

# CppDoc

> :open_book: Powerful tool for analyzing C++ code and docs generation

Generates full documentation with list of all C++ entities in the code.

Supported entities:

- [x] Class
- [x] Structs
- [x] Include
- [x] Templates
- [x] Functions

# Usage

```sh
$> ./bin/cppdoc [-h] [--file FILE] [--module MODULE] [--project PROJECT] [--output OUTPUT]

Optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Path to file.
  --module MODULE, -m MODULE
                        Path to module.
  --project PROJECT, -p PROJECT
                        Path to project.
  --output OUTPUT, -o OUTPUT
                        Output result.
  --version             show programs version number and exit.
```

Generate documentation for **file**.

```sh
$> ./bin/cppdoc --file=<FILE> --output=<OUTPUT>
```

Generate documentation for **module**.

```sh
$> ./bin/cppdoc --module=<MODULE> --output=<OUTPUT>
```

Generate documentation for **project**.

```sh
$> ./bin/cppdoc --project=<PROJECT> --output=<OUTPUT>
```

# License

Project released under the terms of the MIT [license][license].