---
title: "Topic 5: Removing files and directories"
date: 2026-11-10
draft: false
weight: 5
summary: "rmdir for empty directories, rm for files, rm -r for directories with their content, why rm -rf is for ever, and the rm -i safety net for root on RHEL 10."
---

`rmdir` removes a directory, **only if it is empty**:

```console
$ rmdir somedir
rmdir: failed to remove 'somedir': Directory not empty
```

`rm file` removes a file. For a directory with its content you need **`-r`**:

```console
$ rm -rf renamed
$ ls
backup
somedir
```

`rm -rf /path/to/directory` **deletes the dir with its content, for ever**. There's no recycle bin on the command line, and `-f` means no questions asked. Read the path twice before you press Enter.

On RHEL 10, for root, `rm` is an alias for `rm -i`, so it asks before each delete. That's a safety net: only skip it with `-f` when you are sure.

{{< lesson-nav >}}
