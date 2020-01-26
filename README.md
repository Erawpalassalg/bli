```text
  _     _ _ 
 | |   | (_)
 | |__ | |_ 
 | '_ \| | |
 | |_) | | |
 |_.__/|_|_|
```

# bli

**bli** is a simple cli tool to keep a journalised todo list.

It uses the bullet journal notation system and keeps an archive as `.txt` files, so everything will always be readable and accessible.


## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bli.

```bash
pip install bli
```

## Usage
```
$ bli --help

Options:
  --all / --no-all
  -f, --filter TEXT
  -a, --add TEXT
  -x, --cross INTEGER
  -r, --restore INTEGER
  -v, --check INTEGER
  -pp, ->, --postpone INTEGER
  --help                       Show this message and exit.
```

Use the flags `-a|--add`, `-x|--delete`, `-v|--check` and `-pp|--postpone` to manage your tasks 


```bash
$ bli --add "Do whatever" -a "Do something else" -a "Do It Now Said Shia LaBoeuf"
0 • Do whatever
1 • Do something else
2 • Do It Now Said Shia LaBoeuf
```
```bash
$ bli -v 0 -x 1
2 • Do It Now Said Shia LaBoeuf
```
```
$ bli --all
0 v Do whatever
1 x Do something else
2 • Do It Now Said Shia LaBoeuf
```

Entries can be filtered using a string or a regex. Every filtering is **case-insensitive**.

```
$ bli -f '/shia|whatever/' --all
0 v Do whatever
2 • Do It Now Said Shia LaBoeuf
```

Then the next day, every undone task will automatically be postponed and available to the new page. 

```bash
$ bli
0 • Do It Now Said Shia LaBoeuf
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
