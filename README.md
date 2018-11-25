# cppdoc

> Command Line Tool for documentation generation.

# Demo

![Demo](./resources/demo.gif)

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
