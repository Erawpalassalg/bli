```text
       _ _ 
      | (_)
   ___| |_ 
  / __| | |
 | (__| | |
  \___|_| |
       _/ |
      |__/ 
```

# clj

clj is a minimal cli bullet-journal (bujo) written in Python

It keeps an archive as dated `.txt` files so everything you did will always be readable and accessible (at the very least in a `~/.clj` folder).

It automatically postpones undone tasks to the next day.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install clj.

```bash
pip install clj
```

## Usage
```bash
$ clj --help
Usage: clj [OPTIONS]

  Command Line Joural, a minimal CLI bullet journal

Options:
  --all / --no-all (default)
  -f, --filter TEXT
  -a, --add TEXT
  -x, --cross INTEGER
  -r, --restore INTEGER
  -v, --check INTEGER
  --help                 Show this message and exit.

```

The workflow is quite simple:
```bash
$ clj --add "Do whatever" -a "Do something else" -a "Shia LaBoeuf"
0 • Do whatever
1 • Do something else
2 • Shia LaBoeuf
```
```bash
$ clj -v 0 -x 1
2 • Shia LaBoeuf
```
```
$ clj --all
0 v Do whatever
1 x Do something else
2 • Shia LaBoeuf
```
Then the next day, every undone task will automatically be postponed and available to the new page. 
```bash
$ clj
0 • Shia LaBoeuf
```

Also entries can be filtered using a string or a regex. Every filtering is **case-insensitive**.

```
$ clj -f '/shia|whatever/' --all
0 v Do whatever
2 • Shia LaBoeuf
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
