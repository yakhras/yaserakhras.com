---
title: "Topic 6: Working with wildcards"
date: 2026-11-10
draft: false
weight: 6
ShowToc: true
TocOpen: false
summary: "What a wildcard is, the three basic ones (*, ? and [ ]), the extra forms of the brackets, and why the shell, not the command, reads the *."
---

> **Q: What is a wildcard?**
>
> A: A **shell feature** that lets you refer to many files in an easy way: one short pattern instead of typing every file name.

In the examples I use `ls`, the command that **lists** the files in a folder (from [topic 1]({{< relref "/linux/managing-files/01-listing" >}})). My practice folder has five files: `cat`, `cut`, `cot`, `coat` and a hidden one, `.hidden`.

## The three wildcards

| Wildcard | Means | Example | Matches |
|---|---|---|---|
| `*` | any characters, any number of them | `ls *` | every file **except hidden ones** |
| `?` | **exactly one** character, no matter what it is | `ls c?t` | cat, cot, cut (not coat) |
| `[auo]` | one character from the list | `ls c[auo]t` | cat, cot, cut |

> **Q: Does `*` mean everything?**
>
> A: Yes, with one exception: names starting with a dot (hidden files) are left out.

```console
$ ls *
cat
coat
cot
cut

$ ls -a
.
..
.hidden
cat
coat
cot
cut
```

`.hidden` only shows up with `ls -a`.

> **Q: Does `?` mean "exists or not"?**
>
> A: No. It means **one character exists, no matter what it is**. That's why `coat` (two letters between c and t) is not matched:

```console
$ ls c?t
cat
cot
cut
```

⚠ This confused me because in **grep** (regular expressions) `?` *does* mean "0 or 1 time" (`colou?r`). Same symbol, different meaning:

| | `?` in wildcards (shell) | `?` in regex (grep) |
|---|---|---|
| means | exactly one character | the previous character 0 or 1 time |
| example | `c?t` → cat, cut | `colou?r` → color, colour |

## Are there more than three?

> **Q: How many wildcards are there? We just listed three, are there more?**
>
> A: These three are the basics the book covers, and they are enough for daily work and for the exam. But the square brackets `[ ]` have more forms. To test them I added one more file, `file1`, to the practice folder:

| Pattern | Means | Example | Matches |
|---|---|---|---|
| `[a-o]` | one character from a **range** | `ls c[a-o]t` | cat, cot |
| `[!a]` (or `[^a]`) | one character that is **not** in the list | `ls c[!a]t` | cot, cut |
| `[[:digit:]]` | one character from a **class** (also `[:upper:]`, `[:lower:]`, `[:alpha:]`) | `ls file[[:digit:]]` | file1 |

```console
$ ls c[a-o]t
cat
cot

$ ls c[!a]t
cot
cut

$ ls file[[:digit:]]
file1
```

⚠ The curly braces `{ }` look similar, but they are **not** a wildcard. They are **brace expansion**: the shell builds the names from the list, **whether the files exist or not**:

```console
$ echo c{a,u}t dog{1,2}
cat cut dog1 dog2
```

There are no `dog` files in my folder, but the names were still created. That makes braces useful for creating many files at once (`touch dog{1,2}`), not for finding existing ones.

## The shell expands the wildcard before the command runs

The important word for me in the definition was **shell**. The wildcard belongs to the **shell**, not to the **command** itself. So who actually reads the `*`? I tested it with `echo`, a command that only prints what it gets:

```console
$ echo *
cat coat cot cut
```

`echo` knows nothing about files, but it printed my file names. That's because **Bash replaced `*` with the list of names first**, and only then ran `echo`. The command **never** sees the `*`.

> **Q: So can wildcards be used with all commands, not only `ls`?**
>
> A: Technically yes: the shell expands them for any command. But they only **make sense** with commands that expect a **file or folder name** as input, like the ones from the previous topics: listing (`ls`), copying (`cp`), moving (`mv`) and deleting (`rm`).

{{< lesson-nav >}}
