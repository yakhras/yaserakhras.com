---
title: "grep: Find any text in Linux"
date: 2026-10-16
draft: false
tags: ["linux", "rhcsa", "grep", "regex"]
ShowCodeCopyButtons: true
summary: "What grep means, then regular expressions explained step by step: anchors, wildcards, extended regex, the options worth knowing, and a real-world recipe. Every example comes with its actual output."
---

## What does "grep" mean?

The name comes from a command in `ed`, one of the first Unix text editors:

```text
g/re/p
```

- **g**: *global*, so do this on every line of the file
- **re**: a *regular expression*, the pattern to look for
- **p**: *print* the lines that match

So **grep** = **G**lobal **R**egular **E**xpression **P**rint. That's exactly what it still does: it reads text line by line and prints every line that matches your pattern.

You'll also see grep expanded as **General Regular Expression Parser**. It isn't the original meaning, but it describes the job well. A **parser** is a program that reads input and breaks it into parts it understands. grep "parses" your pattern, working out which characters are plain text and which are special symbols like `^`, `$` or `*`. It then checks each line of text against that pattern.

---

I'm preparing for the RHCSA 10 exam and working through Chapter 4 of the *Red Hat RHCSA 10 Cert Guide*. This post turns my marked-up pages into a guide I can come back to. It explains every idea, and every example shows the output it really produces.

![grep: Find any text in Linux, in five steps](infographic.png)

## The practice files

So you can follow along, here are the two small files most examples use (Step 3 adds a few tiny word lists). The first is a cut-down copy of `/etc/passwd`, the file where Linux keeps its user accounts:

```text
root:x:0:0:root:/root:/bin/bash
daemon:x:2:2:daemon:/sbin:/sbin/nologin
anna:x:1000:1000::/home/anna:/bin/bash
linda:x:1001:1001::/home/linda:/bin/zsh
annabel:x:1002:1002::/home/annabel:/bin/bash
joanna:x:1003:1003::/home/joanna:/bin/bash
```

Each line is one user, with fields separated by colons. The first field is the username and the last is the user's shell.

The second is a short version of `/etc/services`, a config file that mixes comments, blank lines and real settings:

```text
# /etc/services: network services list
#
# service-name  port/protocol  [aliases ...]

ssh             22/tcp
# 23 is telnet, avoid it
http            80/tcp          www

https           443/tcp
```

---

## Step 1: What is a regular expression?

`grep` prints every line that contains what you're looking for:

```console
$ grep anna passwd
anna:x:1000:1000::/home/anna:/bin/bash
annabel:x:1002:1002::/home/annabel:/bin/bash
joanna:x:1003:1003::/home/joanna:/bin/bash
```

That's three results, though we only wanted the user *anna*. A plain word isn't precise enough. A **regular expression** (regex) is a search pattern that describes *where* and *how* text should appear, not just *what* it is.

---

## Step 2: Anchors, or where in the line

### `^` means "the line starts with"

```console
$ grep ^anna passwd
anna:x:1000:1000::/home/anna:/bin/bash
annabel:x:1002:1002::/home/annabel:/bin/bash
```

`joanna` is gone, because "anna" isn't at the start of its line. `annabel` is still there, because her line does start with "anna". To match exactly the user anna, anchor on the colon that ends the username:

```console
$ grep ^anna: passwd
anna:x:1000:1000::/home/anna:/bin/bash
```

### `$` means "the line ends with"

Which users have bash as their shell? The shell is the last field, so anchor to the end:

```console
$ grep bash$ passwd
root:x:0:0:root:/root:/bin/bash
anna:x:1000:1000::/home/anna:/bin/bash
annabel:x:1002:1002::/home/annabel:/bin/bash
joanna:x:1003:1003::/home/joanna:/bin/bash
```

`linda` uses zsh and `daemon` uses nologin, so neither appears.

### `^$` means an empty line

Put the two anchors together with nothing between them and you get "a line that starts and immediately ends", in other words a **blank line**:

```console
$ grep -c '^$' services
2
```

(`-c` counts the matching lines instead of printing them.) We'll use this in the final recipe.

---

## Step 3: Wildcards and repetition

These symbols describe **which** characters can stand in a spot and **how many times**. Each card below shows what the symbol means, when to reach for it, what it matches (green) and what it doesn't (red), and the real output.

| Symbol | In short | Needs `-E`? |
|---|---|---|
| `.` | any one character | no |
| `[ ]` | one character from a list | no |
| `?` | maybe there, maybe not | yes |
| `*` | 0 or more of the previous character | no |
| `.*` | anything, or nothing | no |
| `+` | 1 or more of the previous character | yes |
| `{n}` | exactly *n* of the previous character | yes (or `\{n\}`) |

The examples use four tiny practice files: `rd` (red, rad, r1d, r d, r-d, rd, reed), `gr` (gray, grey, griy, gr8y), `words` (color, colour, colouur, red, reed, reeed) and `urls` (http://a, https://b, httpss://c).

### `.`: any one character

{{< regex pattern="r.d" means="exactly **one** character, and it can be **anything**: a letter, a digit, a space or a symbol" use="you know how long the text is, but not which character is in that spot." yes="red|rad|r1d|r d|r-d" no="rd|reed" >}}
```console
$ grep 'r.d' rd
red
rad
r1d
r d
r-d
```
`rd` has nothing between r and d, and `reed` has two characters there. The dot always means exactly one. For two, write `r..d`.
{{< /regex >}}

### `[ ]`: one character from your list

{{< regex pattern="gr[ae]y" means="**one** character, but only one that's in the list" use="only certain characters are allowed in that spot." yes="gray|grey" no="griy|gr8y" >}}
The list can be **any length**: 1, 2, 5 or a whole range. It **always fills one position**:

| List | Allows | `gr…y` matches |
|---|---|---|
| `[a]` | only a (same as writing `a`) | gray |
| `[ae]` | a or e | gray, grey |
| `[aeiou]` | any vowel | gray, grey, griy |
| `[0-9]` | any digit | gr8y |
| `[^ae]` | anything **except** a or e | griy, gr8y |

```console
$ grep 'gr[aeiou]y' gr
gray
grey
griy

$ grep 'gr[^ae]y' gr
griy
gr8y
```
Common ranges: `[a-z]`, `[A-Z]`, `[0-9]`, `[a-zA-Z0-9]`.
{{< /regex >}}

### `?`: maybe there, maybe not

{{< regex pattern="colou?r" means="the previous character appears **0 or 1** time" use="you're not sure whether a character is there, and you want both versions." yes="color|colour|http://|https://" no="colouur|httpss://" ere="true" >}}
```console
$ grep -E 'colou?r' words
color
colour

$ grep -E 'https?://' urls
http://a
https://b
```
`?` allows at most one, so `colouur` and `httpss://` are left out.
{{< /regex >}}

### `*`: zero or more

{{< regex pattern="colou*r" means="the previous character, **any number of times, including zero**" use="a character may be missing, or repeated any number of times." yes="color|colour|colouur" no="colr" >}}
```console
$ grep 'colou*r' words
color
colour
colouur
```
`*` only repeats the **one** character before it, here the "u". `colr` is missing the second "o" (`colou*r` needs "colo" first), so it doesn't match.
{{< /regex >}}

### `.*`: anything, or nothing

{{< regex pattern="^anna.*bash$" means="**any characters, any number, even none**: a dot repeated by a star" use="the text in between repeats, or simply doesn't matter to you." yes="anna:x:1000…/bin/bash|annabel:x:1002…/bin/bash" no="linda…/bin/zsh|joanna…/bin/bash" >}}
```console
$ grep '^anna.*bash$' passwd
anna:x:1000:1000::/home/anna:/bin/bash
annabel:x:1002:1002::/home/annabel:/bin/bash
```
Read it as: starts with "anna", *whatever*, ends with "bash". `linda` ends with zsh, and `joanna` doesn't start with "anna".
{{< /regex >}}

### `+`: one or more

{{< regex pattern="colou+r" means="the previous character, **at least once**" use="a character must be there, but it may repeat." yes="colour|colouur" no="color" ere="true" >}}
```console
$ grep -E 'colou+r' words
colour
colouur
```
Like `*`, but zero isn't allowed, so `color` (no "u") is left out.
{{< /regex >}}

### `{n}`: an exact number of times

{{< regex pattern="re{2}d" means="the previous character, **exactly n** times" use="you know exactly how many times a character repeats." yes="reed" no="red|reeed" ere="true" >}}
| Form | Means | Matches |
|---|---|---|
| `e{2}` | exactly 2 | reed |
| `e{1,2}` | 1 or 2 | red, reed |
| `e{2,}` | 2 or more | reed, reeed |
| `e{1}` | exactly 1: **adds nothing**, same as plain `e` | red |

```console
$ grep -E 're{2}d' rd
reed

$ grep 're\{2\}d' rd
reed
```
Without `-E`, the braces need backslashes (`\{2\}`), which is how the book writes it. Both commands above do the same thing.
{{< /regex >}}

Most of these cards say **needs grep -E**. That's the next step.

---

## Step 4: Basic vs. extended regex (`grep -E`)

Linux has two sets of regular expressions:

- **Basic** regex, which plain `grep` understands: `^ $ . * [ ]`
- **Extended** regex, which adds `? + { } ( ) |`

Plain `grep` treats extended symbols as ordinary characters. This caught me out:

```console
$ printf 'reed\nre{2}d\n' | grep 're{2}d'
re{2}d
```

Without `-E`, grep looked for the literal text `re{2}d`. With `-E` it understands the pattern and finds `reed`.

**grep -E vs. egrep:** you'll see both in older guides. `grep -E` is the modern way. `egrep` is the old way, and behind the scenes it's just a two-line script that runs `grep -E`. Newer grep versions print a warning that it's obsolescent, so stick with `grep -E`.

### Reading a real pattern: `web(/.*)?`

This pattern comes from SELinux file-context rules. Read it from left to right:

1. `web`: the literal text "web"
2. `(/.*)`: a group, made of a slash followed by `.*`, which means "anything, any length"
3. `?`: that whole group may appear **0 or 1** time

So it matches the directory itself, the directory with a trailing slash, and anything inside it:

```console
$ grep -E '^web(/.*)?$' paths
web
web/
web/index.html
```

`website` doesn't match. After "web" comes "s", not a slash and not the end of the line.

---

## Step 5: The options you'll use every day

| Option | What it does | Example | Returns |
|---|---|---|---|
| `-i` | **i**gnore upper/lower case | `grep -i ROOT passwd` | the `root:x:0:0:…` line, even though you typed ROOT |
| `-v` | in**v**ert: show lines that do **not** match | `grep -v nologin passwd` | 5 users: everyone except `daemon` |
| `-n` | show line **n**umbers | `grep -n anna passwd` | `3:anna…`, `5:annabel…`, `6:joanna…` |
| `-c` | **c**ount matching lines | `grep -c 'bash$' passwd` | just the number `4` |
| `-r` | **r**ecursive: search every file in a directory and its subdirectories | `grep -r port .` | `sub/sshd.conf:port 22` and `web.conf:port 80` |
| `-l` | **l**ist only the names of matching files | `grep -rl port .` | `./sub/sshd.conf` and `./web.conf`, no line text |
| `-e` | add another **e**xpression (pattern) | `grep -e '^ssh' -e '^http' services` | the `ssh`, `http` and `https` lines |
| `-E` | **E**xtended regex | `grep -E 'colou?r' words` | `color` and `colour` |
| `-A n` | also show *n* lines **A**fter each match | `grep -A1 '^ssh' services` | the `ssh` line + the comment line under it |
| `-B n` | also show *n* lines **B**efore each match | `grep -B1 '^https' services` | the blank line above + the `https` line |
| `-w` | match **w**hole words only | `grep -w anna passwd` | only the `anna` line, not `annabel` or `joanna` |
| `-o` | print **o**nly the matching part | `grep -o 'bash$' passwd` | `bash`, 4 times |
| `-h` | **h**ide file names (with `-r` or many files) | `grep -rh port .` | `port 22` and `port 80` |
| `-I` | skip binary files | `grep -rI word .` | text files only, no "Binary file … matches" |

The letter of each option comes from the bold part of its description, which makes them easier to remember.

A few with their output:

```console
$ grep -i ROOT passwd
root:x:0:0:root:/root:/bin/bash

$ grep -n anna passwd
3:anna:x:1000:1000::/home/anna:/bin/bash
5:annabel:x:1002:1002::/home/annabel:/bin/bash
6:joanna:x:1003:1003::/home/joanna:/bin/bash

$ grep -v nologin passwd
root:x:0:0:root:/root:/bin/bash
anna:x:1000:1000::/home/anna:/bin/bash
linda:x:1001:1001::/home/linda:/bin/zsh
annabel:x:1002:1002::/home/annabel:/bin/bash
joanna:x:1003:1003::/home/joanna:/bin/bash
```

`grep -v nologin` is a quick way to list the accounts that can actually log in.

### `-r` without a directory

If you give `-r` a pattern but **no directory**, grep searches the directory you're currently in (and everything below it). Here I'm inside a folder that holds `web.conf` and `sub/sshd.conf`:

```console
$ grep -r port
sub/sshd.conf:port 22
web.conf:port 80
```

That's the same as `grep -r port .`, where `.` means "the current directory". Add `-n` to see line numbers as well:

```console
$ grep -rn port .
./sub/sshd.conf:1:port 22
./web.conf:1:port 80
```

---

## Putting it together: read a config file without the noise

Config files on Linux are mostly comments. To see only the settings, start by hiding the comment lines with `-v '^#'`:

```console
$ grep -v '^#' services

ssh             22/tcp
http            80/tcp          www

https           443/tcp
```

That's better, but blank lines are left behind. Add a second pattern with `-e` to hide those as well:

```console
$ grep -v -e '^#' -e '^$' services
ssh             22/tcp
http            80/tcp          www
https           443/tcp
```

Only the real settings are left. On a real system this works the same way with `/etc/services`, `/etc/ssh/sshd_config` or almost any other config file.

---

{{< box >}}
## Real-life examples: searching source code

The output is real, cut short with `…` where it was long.

### Find any of several words: `\|`

```console
$ grep -rn "group_ids\|groups_id"
```

- `\|` means **OR**: match `group_ids` or `groups_id`. It's two symbols: the bar `|` is the OR, and the backslash `\` in front of it is there because we didn't use `-E`. Plain grep uses basic regex, where a bare `|` is just an ordinary character, so the backslash is what turns it into OR. With `-E` you write the bar alone, `|` (see the next example).
- It isn't limited to two words. Add one `\|` per extra word: `grep -rn "one\|two\|three"` finds lines with any of the three.
- `-rn`: search every file in the current folder, and show line numbers so you can jump straight there.

The same in one file:

```console
$ grep -n 't-ref\|canvas' views/graph/graph_renderer.xml
```

Tip: if you catch yourself writing `'Ref\|ref'`, use `-i ref` instead. It ignores upper and lower case for you.

### The same with `-E`, over many files

```console
$ grep -nE 'record id=|<menuitem' views/*.xml data/*.xml
```

- With `-E`, a plain `|` means OR, no backslash needed.
- `views/*.xml data/*.xml`: `*` means **any file name**, so `views/*.xml` is every file ending in `.xml` inside the `views` folder, whatever it's called (`menus.xml`, `goatcounter_views.xml`, …). The shell (not grep) turns each `*` into that list of files, so grep searches all of them. Every line starts with its file name.

### Group the part that changes: `( )`

```console
$ grep -nE 'name="(journey|country_id|pageview_ids)"' views/goatcounter_visit_views.xml
```

Read it as: `name="`, then **one of** the three names, then `"`. The brackets hold only the part that changes, so you don't have to write `name="…"` three times. The quotes on both sides also make it exact: `name="journey_count"` wouldn't match. With only one file, grep doesn't print the file name.

### Find where a function is defined, and why `.*` can trick you

```console
$ grep -rn 'export.*useRef' .
```

This finds lines, but none of them is the definition of `useRef`. `.*` accepts *anything* in between, so `this.exportListRef = useRef(` matches too: "export" sits inside `exportListRef`, and "useRef" comes later on the line. The loose part matched far more than I meant.

Be precise instead. `-w` matches **whole words only**, so `useRefListener` no longer counts:

```console
$ grep -rnw 'function useRef' .
./lib/owl/owl.js:6216:    function useRef(name) {
```

One line, the real definition. When `.*` gives you noise, replace it with the exact text you expect.

### Print only the matching part: `-o` and `-h`

```console
$ grep -rhoE 't-(esc|out|if|foreach)="[a-zA-Z_.]+' web/static/src/views | head -5
t-out="noContentHelp
t-if="title
t-esc="title
t-if="description
t-esc="description
```

- `-o`: print **only** the part that matched, not the whole line.
- `-h`: **h**ide the file names.
- `t-(esc|out|if|foreach)="`: one of the four commands, then `="`.
- `[a-zA-Z_.]+`: one or more letters, underscores or dots, so the name after it (`props.string`, `title`). It stops at the first other character, like `(` or a space.
- `| head -5`: show only the first 5 lines. There were 615.

Now the real use: count them. `sort` puts equal lines together, `uniq -c` counts each one, and `sort -rn` puts the biggest number first:

```console
$ grep -rhoE 't-(esc|out|if|foreach)="[a-zA-Z_.]+' web/static/src/views | sort | uniq -c | sort -rn | head -3
     26 t-if="props.readonly
     16 t-if="props.record.data
     13 t-esc="formattedValue
```
{{< /box >}}

---

## Cheat sheet

| Goal | Command |
|---|---|
| Lines starting with X | `grep '^X' file` |
| Lines ending with X | `grep 'X$' file` |
| Optional character | `grep -E 'colou?r' file` |
| Case-insensitive | `grep -i word file` |
| Everything except X | `grep -v X file` |
| Search a whole directory | `grep -r word /etc` |
| Config without comments and blanks | `grep -v -e '^#' -e '^$' file` |
| Either of two words, whole project | `grep -rnIE 'old_name\|new_name' .` |
| One of several names in the same spot | `grep -nE 'name="(a\|b\|c)"' file` |
| Count every different match | `grep -rhoE 'pattern' . \| sort \| uniq -c \| sort -rn` |

---

*Based on: Red Hat RHCSA 10 Cert Guide, Chapter 4. Explanations and examples are my own, and every command was run on GNU grep with the output shown above.*
