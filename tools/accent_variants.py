"""Προσθέτει παραλλαγές χωρίς τόνο στις φράσεις των conversation triggers.

Το HA Cloud STT συχνά γράφει λέξεις χωρίς τόνο («ενισχυτη»), και οι sentence triggers συγκρίνουν τους τόνους
κατά γράμμα. Το εργαλείο κάνει κάθε τονισμένη λέξη «(λέξη|λεξη)» μέσα στις γραμμές κάτω από `command:`.
Είναι idempotent: ό,τι έχει ήδη παραλλαγή μένει ως έχει. Τα {wildcards} δεν αγγίζονται.

Χρήση (από τη ρίζα του repo):
    python3 tools/accent_variants.py packages            # dry run: δείχνει πόσες αλλαγές ανά αρχείο
    python3 tools/accent_variants.py packages --apply    # γράφει τα αρχεία

Τρέξ' το ξανά κάθε φορά που προσθέτεις φράσεις.
"""
import pathlib
import re
import sys

ACC = str.maketrans("άέήίόύώϊΐϋΰΆΈΉΊΌΎΏΪΫ", "αεηιουωιιυυΑΕΗΙΟΥΩΙΥ")
WORD = re.compile(r"[A-Za-zΑ-Ωα-ωΆ-Ώά-ώϊϋΐΰΪΫ]+")


def plain(w):
    return w.translate(ACC)


def transform(cmd):
    """Μετατρέπει μία φράση. Αγνοεί {…} και λέξεις που έχουν ήδη παραλλαγή."""
    out, i = [], 0
    while i < len(cmd):
        if cmd[i] == "{":
            j = cmd.index("}", i) + 1
            out.append(cmd[i:j])
            i = j
            continue
        m = WORD.match(cmd, i)
        if not m:
            out.append(cmd[i])
            i += 1
            continue
        w = m.group(0)
        p = plain(w)
        j = m.end()
        already = cmd[i - 1:i] == "(" and cmd[j:j + len(p) + 2] == f"|{p})"
        if p != w and not already:
            out.append(f"({w}|{p})")
        else:
            out.append(w)
        i = j
    return "".join(out)


def process(path, apply):
    raw = path.read_text(encoding="utf-8").split("\n")
    # Ένωση γραμμών-συνέχειας (plain scalars που το YAML έσπασε σε δύο γραμμές) μέσα σε λίστες command
    lines, in_c, item_ind, c_ind = [], False, -1, 0
    for ln in raw:
        s, ind = ln.strip(), len(ln) - len(ln.lstrip())
        if s.startswith("command:"):
            in_c, item_ind, c_ind = True, -1, ind
        elif in_c and s.startswith("- ") and ind >= c_ind:
            item_ind = ind
        elif in_c and s and item_ind >= 0 and ind > item_ind and not s.startswith("#") and lines:
            lines[-1] = lines[-1].rstrip() + " " + s
            continue
        elif in_c and s and not s.startswith("#"):
            in_c = False
        lines.append(ln)
    changed = 0
    in_cmd = False
    cmd_indent = 0
    for n, ln in enumerate(lines):
        s = ln.strip()
        ind = len(ln) - len(ln.lstrip())
        if s.startswith("command:"):
            in_cmd = True
            cmd_indent = ind
            rest = s[len("command:"):].strip()
            if rest:  # command: "..." ή [ ... ] σε μία γραμμή
                in_cmd = False
                if rest.startswith("[") and rest.endswith("]"):
                    items = re.findall(r'"([^"]*)"', rest)
                    new = rest
                    for it in items:
                        new = new.replace(f'"{it}"', f'"{transform(it)}"', 1)
                elif rest.startswith('"'):
                    new = f'"{transform(rest.strip(chr(34)))}"'
                else:
                    new = f'"{transform(rest)}"'
                if new != rest:
                    lines[n] = ln[: ln.index("command:")] + "command: " + new
                    changed += 1
            continue
        if in_cmd:
            if s.startswith("- ") and ind >= cmd_indent:
                body = s[2:]
                q = body[0] if body[:1] in "\"'" else ""
                text = body[1:-1] if q else body
                new = transform(text)
                if new != text:
                    lines[n] = ln[: ind] + '- "' + new.replace('"', '\\"') + '"'
                    changed += 1
                continue
            if s and not s.startswith("#"):
                in_cmd = False
    if apply and changed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return changed


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "packages")
    apply = "--apply" in sys.argv
    total = 0
    for f in sorted(root.rglob("*.yaml")):
        c = process(f, apply)
        if c:
            print(f"{f}: {c} φράσεις")
            total += c
    print(f"\n{'ΕΦΑΡΜΟΓΗ' if apply else 'DRY RUN'}: {total} φράσεις")
