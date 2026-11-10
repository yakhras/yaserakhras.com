---
title: "Topic 4: Moving files and directories"
date: 2026-11-10
draft: false
weight: 4
summary: "mv moves and renames with the same command, moves a whole directory without -r, and is instant on the same filesystem."
---

`mv` moves a file to a new location. The same command **renames**: a rename is just a move to a new name in the same place. Here I rename `newcopy`, the copy from [topic 3]({{< relref "/linux/managing-files/03-copying" >}}):

```console
$ mv newcopy renamed
$ ls
backup
renamed
somedir
```

| Command | Does |
|---|---|
| `mv myfile /tmp` | moves myfile to /tmp |
| `mv somefiles /tmp` | moves a directory, with its content (no `-r` needed) |
| `mv myfile mynewfile` | renames |

*Footnote:* the book says mv is "nothing else than copying and deleting". That's true when you move between **different filesystems**. On the same filesystem, mv only changes the name and location record, so it's instant, even for a huge file.

{{< lesson-nav >}}
