# my-aws-scripts

A collection of utility scripts designed to streamline tasks and operations on AWS.

## Prerequisites

- Python 3.11.3
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [go-task](https://taskfile.dev/installation/)
- [peco](https://github.com/peco/peco)
- [rye](https://rye-up.com/guide/installation/)

## Setup

```sh
$ git clone git@github.com:MasashiFukuzawa/my-aws-scripts.git
$ cd my-aws-scripts
$ rye sync
```

## How to use linter/formatter

```sh
# exec formatter
$ task fmt -- .
# exec linter
$ task lint -- .
# only check
$ task check-all
```
