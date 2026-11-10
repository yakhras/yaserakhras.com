---
title: "Managing files and folders in Linux"
date: 2026-11-10
draft: false
tags: ["linux", "rhcsa", "files", "bash"]
summary: "The everyday file jobs on Linux: listing, creating, copying, moving and removing files and folders, using wildcards and absolute and relative paths, and other topics that I stand on during my journey while preparing for the RHCSA exam."
description: "The everyday file jobs on Linux: listing, creating, copying, moving and removing files and folders, using wildcards and absolute and relative paths, and other topics that I stand on during my journey while preparing for the RHCSA exam."
cover:
  image: cover.png
  alt: "Managing files and folders in Linux: listing, creating, copying, moving and removing files and folders, using wildcards and absolute and relative paths"
  relative: true
  hiddenInSingle: true
cascade:
  ShowCodeCopyButtons: true
---

I'm working through Chapter 3 of the *Red Hat RHCSA 10 Cert Guide*, the section "Managing Files". While reading I wrote my questions in the margins. This blog keeps those questions, the answers I found, and real output for every command, so I can come back to it.

{{< figure src="infographic.png" alt="Managing files in Linux, in seven steps" class="infographic" >}}

As an administrator, these are the **common file management tasks** you need:

1. Listing files and directories
2. Creating files and directories
3. Copying files and directories
4. Moving files and directories
5. Removing files and directories
6. Working with wildcards
7. Working with absolute and relative pathnames

The last topic, the wrap-up, puts together the `-r` rule and a **cheat sheet** of everything.

All the examples ran in a practice folder (`/tmp/lab`) in Bash, with GNU coreutils. The topics build on each other: the files created in one topic are used in the next.

**[Start with topic 1 »]({{< relref "/linux/managing-files/01-listing" >}})** · Short on time? Go to the [cheat sheet]({{< relref "/linux/managing-files/08-wrap-up#cheat-sheet" >}}).
