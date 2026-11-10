---
title: "Topic 3: Copying files and directories"
date: 2026-11-10
draft: false
weight: 3
ShowToc: true
TocOpen: false
summary: "The cp trap where a missing directory becomes a file, the trailing / that fixes it, copying directories with -r and -a, and the one dot that copies only the content."
---

Basic form: `cp <source> <destination>`.

The book's examples use the users' folders under `/home`. I didn't want to touch the real `/home`, so I built a small copy of it inside my practice folder, and I work from inside it (`/tmp/lab/home`):

```text
/tmp/lab/home
├── lara          (empty folder)
└── lisa
    └── file1
```

## The trap: a missing directory becomes a file

If you copy a file to a directory that **doesn't exist**, cp doesn't complain. It creates a **file** with that name. Here I meant `lara` but typed `lsra`:

```console
$ cp lisa/file1 lsra

$ ls -l
total 1
drwxr-xr-x 1 y.akhras 1049089 0 Nov  4 17:33 lara
drwxr-xr-x 1 y.akhras 1049089 0 Nov  4 17:33 lisa
-rw-r--r-- 1 y.akhras 1049089 3 Nov  4 17:33 lsra
```

No error, and `lsra` is a file (`-`), not a directory (`d`). The file was **duplicated and renamed** to the name of a directory that doesn't exist.

## The fix: end the directory with `/`

The trailing `/` tells cp: **"this must be a directory"**. If it isn't there, you get an error right away instead of a wrong file:

```console
$ cp lisa/file1 lsra/
cp: cannot create regular file 'lsra/': Not a directory

$ cp lisa/file1 lara/
$ ls lara
file1
```

One extra character makes cp **stop** instead of quietly doing the wrong thing. I now always write it.

## Many files into one name

```console
$ cp docs/*.txt Backup
cp: target 'Backup' is not a directory
```

The shell turned `*.txt` into two files, and cp **can't merge multiple files into one file**, so it fails. With an existing `Backup/` directory it works:

```console
$ cp docs/*.txt Backup/
$ ls Backup
a.txt
b.txt
```

⚠ With only **one** `.txt` file there's no error at all: you're back to the trap above, and you get a file called `Backup`. The trailing `/` protects you here too.

## Copying a directory: `-r`

For this part I use a directory called `somedir`. It has a file, a hidden file and a sub-directory inside it:

```console
$ ls -A somedir
.config
notes
sub
```

Without any option, `cp` refuses to copy a directory:

```console
$ cp somedir newcopy
cp: -r not specified; omitting directory 'somedir'
```

`cp` copies a directory with everything inside it only with **`-r`** (recursive). But the result depends on the target, and the command looks the same in both cases:

**Case 1: the target directory exists** → `somedir` is copied **inside** it, with its own name. Here `backup` already exists:

```console
$ mkdir backup
$ cp -r somedir backup
$ ls -A backup
somedir
$ ls -A backup/somedir
.config
notes
sub
```

`backup` now contains the folder `somedir`, and the content is one level deeper. It's the same as the book's example: `cp -r /etc /tmp` gives `/tmp/etc`.

**Case 2: the target doesn't exist** → there is no folder to copy into, so `cp` creates `newcopy` and puts the **content** of `somedir` directly in it. In other words, the directory is **duplicated and renamed**:

```console
$ cp -r somedir newcopy
$ ls
backup
newcopy
somedir
$ ls -A newcopy
.config
notes
sub
```

So the same command `cp -r somedir <target>` gives `backup/somedir/notes` in the first case and `newcopy/notes` in the second. Before copying a directory, check if the target already exists (`ls`), so you know where the files will end up.

## Keep permissions and dates: `-a`

Without options, cp may not keep permissions and other properties. **`-a`** (archive mode) keeps all of them. So `cp -a ~ /tmp` makes an exact copy of your home directory.

## Hidden files, and the most subtle difference in this chapter

By default hidden files are easy to miss. Look at these two commands, which differ by just one dot:

| Command | Result |
|---|---|
| `cp -a /somedir/ .` | copies **the folder with its content** to the current dir |
| `cp -a /somedir/. .` | copies **only the content** (hidden files too) to the current dir |

```console
$ cp -a ../somedir/ .
$ ls -A
somedir

$ cp -a ../somedir/. .
$ ls -A
.config
notes
sub
```

`somedir/.` means "the contents of somedir", and the last `.` is the current directory (note the space between the two dots).

{{< lesson-nav >}}
