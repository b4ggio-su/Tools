import argparse
import sys
import math

__author__ = 'modulo and b4ggio_su'

maxiDic = {
    "a": ["a", "A", "4", "@"],
    "b": ["b", "B", "8"],
    "c": ["c", "C"],
    "d": ["d", "D"],
    "e": ["e", "E", "3"],
    "f": ["f", "F"],
    "g": ["g", "G", "6", "9"],
    "h": ["h", "H"],
    "i": ["i", "I", "1", "!"],
    "j": ["j", "J"],
    "k": ["k", "K"],
    "l": ["l", "L", "1", "!"],
    "m": ["m", "M"],
    "n": ["n", "N"],
    "o": ["o", "O", "0"],
    "p": ["p", "P"],
    "q": ["q", "Q"],
    "r": ["r", "R"],
    "s": ["s", "S", "5", "$"],
    "t": ["t", "T", "7"],
    "u": ["u", "U"],
    "v": ["v", "V"],
    "w": ["w", "W"],
    "x": ["x", "X"],
    "y": ["y", "Y"],
    "z": ["z", "Z", "2"]
}

miniDic = {
    "a": ["4", "@"],
    "e": ["3"],
    "g": ["6", "9"],
    "i": ["1", "!"],
    "l": ["1", "!"],
    "o": ["0"],
    "r": ["2"],
    "s": ["5", "$"],
    "t": ["7", "2"],
    "z": ["2"],
}

specials = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "=", ".", "~", "[", "]", "{", "}", "|",
            ";", ":", "\\" "/", "<", ">", "?"]


def charset_validator(charset):
    def validate(char):
        valid = False
        if charset & 0b0001 > 0:
            valid |= char.islower()

        if charset & 0b0010 > 0:
            valid |= char.isupper()

        if charset & 0b0100 > 0:
            valid |= char.isdigit()

        if charset & 0b1000 > 0:
            valid |= not char.isalpha() and not char.isdigit()

        return valid

    return validate


def substitutions(word, replacements, validator=charset_validator(15)):
    if len(word) == 0:
        yield ""
    else:
        key = word[0].lower()
        options = set([char for char in replacements.get(key, []) if validator(char)])
        options.add(key)
        for c in options:
            for tail in substitutions(word[1:], replacements, validator):
                yield "{}{}".format(c, tail)


def run_mini(words, charset):
    for word in words:
        for c in substitutions(word[0], maxiDic, charset_validator(3)):
            for w in substitutions(word[1:], miniDic, charset_validator(charset)):
                yield c + w


def run_maxi(words, charset):
    for word in words:
        for w in substitutions(word, maxiDic, charset_validator(charset)):
            yield w


def run_addnum(words, count):
    for word in words:
        for i in xrange(count):
            for j in xrange(int(math.ceil(math.log10(count)) + 1)):
                yield '{word}{number:0{length:}d}'.format(word=word, number=i, length=j)


def run_suffix(words, suffix):
    for word in words:
        yield word
        yield word + suffix


def replace(word, indices, special):
    if len(indices) == 0:
        yield word
    else:
        index = indices.pop()
        for s in special:
            for w in replace(word[:index] + s + word[index + 1:], indices, special):
                yield w


def run_replace(words, placeholder):
    for word in words:
        indices = [i for i, ltr in enumerate(word) if ltr == placeholder]
        special = set(specials)
        special.add(placeholder)
        for w in replace(word, indices, special):
            yield w


def run_actions(words, acts):
    if len(acts) == 0:
        for w in words:
            yield w
    else:
        act = acts.pop()
        for w in run_actions(act[0](words, *(act[1])), acts):
            yield w


if __name__ == "__main__":
    words = []

    parser = argparse.ArgumentParser(description='MiniDic - The square wheel of the dictionary generation tools.\
         This script is to provide a flexible framework to support on the fly password list generation.')
    parser.add_argument("-w",
                        metavar="FILE",
                        nargs="?",
                        dest='out',
                        help="Specify output file to write to")
    dict = parser.add_mutually_exclusive_group()
    dict.add_argument("--mini",
                      action="store_true",
                      help="Use MiniDic")
    dict.add_argument("--maxi",
                      action="store_true",
                      help="Use MaxiDic")
    parser.add_argument("--range",
                        metavar="RANGE",
                        type=int,
                        help="The range option adds numbers to the end of all words using a range of 0 to RANGE")
    parser.add_argument("--replace",
                        nargs="?",
                        const="~",
                        help="Permute the selected character (default is ~) with special characters")
    parser.add_argument("--order",
                        nargs="?",
                        default="drns",
                        help="Order to apply mutations in. String: [drns]+")
    parser.add_argument("--suffix",
                        help="The append option adds a string suffix to the end of all words")
    parser.add_argument("--charset",
                        nargs=1,
                        default=15,
                        type=int,
                        choices=range(0,15),
                        help="Select a character set to enable for mutations. Ask Margus....")
    parser.add_argument("words",
                        metavar='word',
                        type=str,
                        nargs="+",
                        help="Input words")
    parser.add_argument("-V", "--version",
                        action='version')
    args = parser.parse_args()

    if args.out is None:
        out = sys.stdout
    else:
        out = open(args.out, 'w')

    acts = []

    def dic():
        if args.mini:
            acts.append((run_mini, [args.charset]))
        elif args.maxi:
            acts.append((run_maxi, [args.charset]))

    def num():
        if args.range is not None:
            acts.append((run_addnum, [args.range + 1]))

    def rep():
        if args.replace is not None:
            acts.append((run_replace, [args.replace]))

    def suf():
        if args.suffix is not None:
            acts.append((run_suffix, [args.suffix]))

    add_actions = {
        'r': rep,
        'd': dic,
        'n': num,
        's': suf
    }

    seen = set()
    order = list(args.order)
    for a in add_actions:
        order.append(a)

    order = [x for x in order if x not in seen and x in add_actions and not seen.add(x)]
    order.reverse()

    for x in order:
        add_actions[x]()

    for w in run_actions(args.words, acts):
        out.write(w + '\n')

    out.close()
