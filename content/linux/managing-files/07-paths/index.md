---
title: "Topic 7: Working with absolute and relative pathnames"
date: 2026-11-10
draft: false
weight: 7
summary: "Where am I? Absolute paths that work from everywhere, relative paths that depend on where you are, and .. to reach a folder next to you."
---

I use the same small copy of `/home` from [topic 3]({{< relref "/linux/managing-files/03-copying" >}}), reset so `lara` is empty again. All the paths below are real ones from my machine:

```text
/tmp/lab/home
├── lara          (empty folder)
└── lisa
    └── file1
```

> **Q: What is the `pwd` command?**
>
> A: Short for **Print Working Directory**. It's the answer to: **"Where am I?"**

```console
$ cd /tmp/lab/home
$ pwd
/tmp/lab/home
```

So right now I am **inside** my copy of `home`. Remember this, the next answers depend on it.

> **Q: What is an absolute pathname?**
>
> A: The complete path to a file, **starting from the root `/`**, then every directory down to the file. Because it starts from the root, it works **no matter where you are**. Here I go to the root `/` first, and the file is still found:

```console
$ cd /
$ pwd
/
$ ls /tmp/lab/home/lisa/file1
/tmp/lab/home/lisa/file1
```

> **Q: What is a relative pathname?**
>
> A: A path that starts **from where you are now**, the directory that `pwd` prints. It **never** starts with `/`. The shell builds the full path by putting the two together:
>
> **where I am** (`/tmp/lab/home`) + `/` + **the relative path** (`lisa/file1`) = `/tmp/lab/home/lisa/file1`

```console
$ cd /tmp/lab/home
$ ls lisa/file1
lisa/file1
```

The same relative path **fails** when I am somewhere else, because the starting point changed:

```console
$ cd /tmp/lab/home/lisa
$ ls lisa/file1
ls: cannot access 'lisa/file1': No such file or directory
```

From inside `lisa` the shell looked for `/tmp/lab/home/lisa/lisa/file1`, which doesn't exist. That's the whole difference: an **absolute** path is the same from everywhere, a **relative** path depends on where you are.

> **Q: And if the place I want is not under me, but next to me?**
>
> A: Use `..`, which means **"the directory one level up"**. Do you remember the `.` and `..` in the `ls -a` output in [topic 6]({{< relref "/linux/managing-files/06-wildcards" >}})? Every directory has these two entries: `.` is the directory itself, and `..` is the one above it.

```console
$ cd /tmp/lab/home/lisa
$ cd ..
$ pwd
/tmp/lab/home
```

So from inside `lisa`, the path `../lara` means: go up one level to `home`, then down into `lara`:

```console
$ cd /tmp/lab/home/lisa
$ cd ../lara
$ pwd
/tmp/lab/home/lara
```

Now, copying `file1` from `lisa` to `lara` can be written three ways, depending on where I am:

| Where I am | Command | Type |
|---|---|---|
| anywhere | `cp /tmp/lab/home/lisa/file1 /tmp/lab/home/lara/` | absolute: always works |
| `/tmp/lab/home` | `cp lisa/file1 lara/` | relative: both folders are under where I am |
| `/tmp/lab/home/lisa` | `cp file1 ../lara/` | relative, going up one level with `..` |

```console
$ cd /tmp/lab/home/lisa
$ cp file1 ../lara/
$ ls ../lara
file1
```

The book's tip, which I agree with: **absolute paths mean more typing, but fewer mistakes.** If you're not sure where you are, use the full path.

{{< lesson-nav >}}
