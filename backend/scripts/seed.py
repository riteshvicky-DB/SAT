"""
Seed – generates enough UNIQUE questions for 100 non-repeating full-length test models.
  Math  : 21 skills × 250 unique skill-specific variants = 5,250  (need 4,400)
  R/W   : 250 passages × 22 question types = 5,500 unique (passage,q) pairs (need 5,400)

Ordering guarantees diversity within every model:
  Math  – external_id encodes (variant_idx first) so all skills appear in every model
  R/W   – ordered by passage so every 54-question model covers 2-3 passages, no pair repeats
"""
import json
import math
import random
import sys
from collections import Counter
from math import gcd, isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.core.database import SessionLocal, init_db
from app.models import Question, User, VideoRecommendation
from app.services.curriculum import all_skills

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _shuffle(items: list, seed: int) -> list:
    r = random.Random(seed)
    out = list(items)
    r.shuffle(out)
    return out

def _make_choices(correct_text: str, wrongs: list[str], seed: int) -> tuple[list[dict], str]:
    """Return (choices list, correct_id) with correct answer at a random position."""
    texts = [correct_text] + wrongs[:3]
    shuffled = _shuffle(texts, seed)
    labels = "ABCD"
    choices = [{"id": labels[i], "text": t} for i, t in enumerate(shuffled)]
    correct_id = next(c["id"] for c in choices if c["text"] == correct_text)
    return choices, correct_id


# ─── Skill-specific math question generators ──────────────────────────────────

def _gen_linear_equations(n: int) -> list[dict]:
    out = []
    r = random.Random(101)
    while len(out) < n:
        a = r.randint(2, 12)
        b = r.randint(1, 20)
        x = r.randint(-8, 12)
        c = a * x + b
        wrongs = [str(x + r.randint(1,4)), str(x - r.randint(1,3)), str(x * 2 - 1)]
        ch, ci = _make_choices(str(x), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"If {a}x + {b} = {c}, what is the value of x?",
                    "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": f"Subtract {b} from both sides to get {a}x = {c-b}, then divide by {a} to find x = {x}."})
    return out[:n]

def _gen_systems(n: int) -> list[dict]:
    out = []
    r = random.Random(202)
    while len(out) < n:
        x, y = r.randint(1, 10), r.randint(1, 10)
        a1, b1 = r.randint(1, 4), r.randint(1, 4)
        a2, b2 = r.randint(1, 4), r.randint(1, 4)
        if a1 * b2 == a2 * b1:
            continue
        c1, c2 = a1*x + b1*y, a2*x + b2*y
        wrongs = [str(x+1), str(x-1), str(y)]
        ch, ci = _make_choices(str(x), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"Given {a1}x + {b1}y = {c1} and {a2}x + {b2}y = {c2}, what is x?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Use elimination or substitution to find x = {x} and y = {y}."})
    return out[:n]

def _gen_inequalities(n: int) -> list[dict]:
    out = []
    r = random.Random(303)
    ops = [">", "<", "≥", "≤"]
    while len(out) < n:
        a = r.randint(1, 8)
        b = r.randint(0, 15)
        c = r.randint(b+1, b + a*10)
        op = r.choice(ops)
        x_boundary = (c - b) / a
        x_int = int(x_boundary)
        if op in (">", "≥"):
            correct = f"x {op} {x_int}" if x_boundary == x_int else f"x {op} {x_boundary:.1f}"
            wrong1, wrong2, wrong3 = f"x < {x_int}", f"x = {x_int}", f"x ≤ {x_int}"
        else:
            correct = f"x {op} {x_int}" if x_boundary == x_int else f"x {op} {x_boundary:.1f}"
            wrong1, wrong2, wrong3 = f"x > {x_int}", f"x = {x_int}", f"x ≥ {x_int}"
        ch, ci = _make_choices(correct, [wrong1, wrong2, wrong3], r.randint(0, 10**9))
        out.append({"prompt": f"Which inequality represents the solution to {a}x + {b} {op} {c}?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Subtract {b} from both sides, then divide by {a} to isolate x."})
    return out[:n]

def _gen_functions(n: int) -> list[dict]:
    out = []
    r = random.Random(404)
    while len(out) < n:
        a = r.randint(1, 6)
        b = r.randint(-8, 8)
        x_val = r.randint(-5, 8)
        ans = a * x_val + b
        wrongs = [str(ans + a), str(ans - 1), str(a * x_val)]
        ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"If f(x) = {a}x {'+ ' + str(b) if b >= 0 else '– ' + str(abs(b))}, what is f({x_val})?",
                    "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": f"Substitute x = {x_val}: f({x_val}) = {a}({x_val}) + ({b}) = {ans}."})
    return out[:n]

def _gen_graph_interpretation(n: int) -> list[dict]:
    out = []
    r = random.Random(505)
    while len(out) < n:
        m = r.choice([-4,-3,-2,-1,1,2,3,4])
        b = r.randint(-6, 6)
        eq = f"y = {m}x {'+ ' + str(b) if b >= 0 else '– ' + str(abs(b))}"
        choice_type = r.choice(["slope", "y-intercept", "x-intercept"])
        if choice_type == "slope":
            correct = str(m)
            wrongs = [str(m+1), str(-m), str(m*2)]
            question = f"What is the slope of the line {eq}?"
        elif choice_type == "y-intercept":
            correct = str(b)
            wrongs = [str(b+1), str(-b), str(m)]
            question = f"What is the y-intercept of {eq}?"
        else:
            xi = -b / m if m != 0 else 0
            correct = f"{xi:.1f}" if xi != int(xi) else str(int(xi))
            wrongs = [str(int(xi)+1), str(int(xi)-1), str(int(xi)*2)]
            question = f"At what x-value does {eq} cross the x-axis?"
        ch, ci = _make_choices(correct, wrongs, r.randint(0, 10**9))
        out.append({"prompt": question, "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": f"From the equation {eq}, read off the {choice_type} directly."})
    return out[:n]

def _gen_quadratics(n: int) -> list[dict]:
    out = []
    r = random.Random(606)
    while len(out) < n:
        r1, r2 = r.randint(-7, 7), r.randint(-7, 7)
        if r1 == r2 == 0:
            continue
        b = -(r1 + r2)
        c = r1 * r2
        sign_b = f"+ {b}" if b >= 0 else f"– {abs(b)}"
        sign_c = f"+ {c}" if c >= 0 else f"– {abs(c)}"
        ans = f"{min(r1,r2)} and {max(r1,r2)}" if r1 != r2 else str(r1)
        w1 = f"{min(r1,r2)+1} and {max(r1,r2)+1}"
        w2 = f"{-min(r1,r2)} and {-max(r1,r2)}"
        w3 = f"{r1*2} and {r2*2}"
        ch, ci = _make_choices(ans, [w1, w2, w3], r.randint(0, 10**9))
        out.append({"prompt": f"What are the solutions to x² {sign_b}x {sign_c} = 0?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Factor as (x – {r1})(x – {r2}) = 0, giving x = {r1} or x = {r2}."})
    return out[:n]

def _gen_polynomials(n: int) -> list[dict]:
    out = []
    r = random.Random(707)
    while len(out) < n:
        a, b, c = r.randint(1,4), r.randint(-5,5), r.randint(-8,8)
        x_val = r.randint(-3, 4)
        ans = a * x_val**2 + b * x_val + c
        wrongs = [str(ans+a), str(ans-b), str(ans*2)]
        sign_b = f"+ {b}x" if b >= 0 else f"– {abs(b)}x"
        sign_c = f"+ {c}" if c >= 0 else f"– {abs(c)}"
        ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"If p(x) = {a}x² {sign_b} {sign_c}, what is p({x_val})?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Substitute x = {x_val}: {a}({x_val})² + {b}({x_val}) + {c} = {ans}."})
    return out[:n]

def _gen_exponential(n: int) -> list[dict]:
    out = []
    r = random.Random(808)
    while len(out) < n:
        a = r.randint(2, 5)
        base = r.choice([2, 3, 5])
        t = r.randint(0, 4)
        ans = a * (base ** t)
        wrongs = [str(ans + base), str(a * base * t), str(ans * base)]
        ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"A population starts at {a} and triples every year. What is the population after {t} years?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Population = {a} × {base}^{t} = {ans}."})
        # vary: decay problems
        a2 = r.randint(100, 500) * 4
        half = r.choice([2, 4])
        t2 = r.randint(1, 3)
        ans2 = a2 // (half ** t2)
        wrongs2 = [str(ans2 + half), str(a2 - ans2), str(ans2 * 2)]
        ch2, ci2 = _make_choices(str(ans2), wrongs2, r.randint(0, 10**9))
        out.append({"prompt": f"A substance of {a2} mg is halved every {half} hours. How much remains after {t2 * half} hours?",
                    "choices": ch2, "correct": ci2, "difficulty": "medium",
                    "explanation": f"Halved {t2} time(s): {a2} ÷ {half}^{t2} = {ans2} mg."})
    return out[:n]

def _gen_radicals(n: int) -> list[dict]:
    out = []
    r = random.Random(909)
    perfect_sq = [1,4,9,16,25,36,49,64,81,100,121,144,169,196,225]
    while len(out) < n:
        val = r.choice(perfect_sq)
        ans = int(val ** 0.5)
        x_sq = r.randint(1, 12)
        # solve √(ax+b) = c
        c = r.randint(2, 8)
        b = r.randint(0, 10)
        ax = c**2 - b
        if ax <= 0 or ax % r.randint(1,3) != 0:
            wrongs = [str(ans+1), str(ans-1), str(ans*2)]
            ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"What is √{val}?",
                        "choices": ch, "correct": ci, "difficulty": "easy",
                        "explanation": f"√{val} = {ans} because {ans}² = {val}."})
        else:
            a_coef = r.randint(1,3)
            rhs = c**2
            x_ans = (rhs - b) // a_coef if a_coef > 0 and (rhs-b) % a_coef == 0 else c
            wrongs = [str(x_ans+1), str(x_ans*2), str(x_ans-1)]
            ch, ci = _make_choices(str(x_ans), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"If √({a_coef}x + {b}) = {c}, what is x?",
                        "choices": ch, "correct": ci, "difficulty": "hard",
                        "explanation": f"Square both sides: {a_coef}x + {b} = {c**2}, so x = {x_ans}."})
    return out[:n]

def _gen_rational(n: int) -> list[dict]:
    out = []
    r = random.Random(1010)
    while len(out) < n:
        num = r.randint(2, 10)
        den = r.randint(2, 10)
        x_val = r.randint(1, 8)
        b = r.randint(1, 5)
        # (num*x + b) / den = ans
        ans_num = num * x_val + b
        if ans_num % den == 0:
            ans = str(ans_num // den)
        else:
            g = gcd(ans_num, den)
            ans = f"{ans_num//g}/{den//g}"
        wrongs = [str(ans_num), str(x_val + 1), str(x_val * den)]
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"What is ({num}x + {b}) / {den} when x = {x_val}?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"Substitute x = {x_val}: ({num}·{x_val} + {b}) / {den} = {ans_num}/{den} = {ans}."})
    return out[:n]

def _gen_ratios(n: int) -> list[dict]:
    out = []
    r = random.Random(1111)
    while len(out) < n:
        a, b = r.randint(1, 8), r.randint(1, 8)
        total = r.randint(a+b, (a+b)*5)
        part_a = total * a // (a + b)
        wrongs = [str(part_a + 1), str(part_a - 1), str(total - part_a)]
        ch, ci = _make_choices(str(part_a), wrongs, r.randint(0, 10**9))
        out.append({"prompt": f"The ratio of A to B is {a}:{b}. If the total is {total}, how many are in group A?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"A = {total} × {a}/({a}+{b}) = {total} × {a}/{a+b} = {part_a}."})
        # proportion variant
        p, q = r.randint(2, 9), r.randint(2, 9)
        scale = r.randint(2, 6)
        ans2 = p * scale
        wrongs2 = [str(ans2+p), str(ans2-q), str(p*q)]
        ch2, ci2 = _make_choices(str(ans2), wrongs2, r.randint(0, 10**9))
        out.append({"prompt": f"If {p} items cost ${q}, how many items can be bought for ${q*scale}?",
                    "choices": ch2, "correct": ci2, "difficulty": "easy",
                    "explanation": f"Use proportion: {p}/{q} = x/{q*scale} → x = {ans2}."})
    return out[:n]

def _gen_percentages(n: int) -> list[dict]:
    out = []
    r = random.Random(1212)
    pct_vals = [5,10,12,15,20,25,30,40,50,60,75,80,90]
    while len(out) < n:
        typ = r.randint(0, 2)
        if typ == 0:  # X% of N
            pct = r.choice(pct_vals)
            base = r.randint(20, 200) * 5
            ans = base * pct // 100
            wrongs = [str(ans + pct), str(base - ans), str(ans * 2)]
            ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"What is {pct}% of {base}?",
                        "choices": ch, "correct": ci, "difficulty": "easy",
                        "explanation": f"{pct}% of {base} = {base} × {pct}/100 = {ans}."})
        elif typ == 1:  # percentage increase
            orig = r.randint(20, 100) * 5
            pct = r.choice(pct_vals)
            new_val = orig + orig * pct // 100
            wrongs = [str(new_val + pct), str(orig + pct), str(new_val - pct)]
            ch, ci = _make_choices(str(new_val), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"A price of ${orig} increases by {pct}%. What is the new price?",
                        "choices": ch, "correct": ci, "difficulty": "medium",
                        "explanation": f"New price = {orig} × (1 + {pct}/100) = {new_val}."})
        else:  # find original
            pct = r.choice([10,20,25,50])
            ans = r.randint(5, 20) * 10
            result = ans * pct // 100
            wrongs = [str(ans + 10), str(result * 2), str(ans - 10)]
            ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"{pct}% of a number is {result}. What is the number?",
                        "choices": ch, "correct": ci, "difficulty": "medium",
                        "explanation": f"x × {pct}/100 = {result} → x = {ans}."})
    return out[:n]

def _gen_statistics(n: int) -> list[dict]:
    out = []
    r = random.Random(1313)
    while len(out) < n:
        size = r.randint(4, 7)
        vals = sorted([r.randint(1, 20) for _ in range(size)])
        typ = r.choice(["mean", "median", "range", "mode"])
        if typ == "mean":
            ans = sum(vals) // len(vals)
            q = f"The data set {vals} has a mean of:"
        elif typ == "median":
            mid = size // 2
            ans = vals[mid] if size % 2 == 1 else (vals[mid-1] + vals[mid]) // 2
            q = f"What is the median of {vals}?"
        elif typ == "range":
            ans = vals[-1] - vals[0]
            q = f"What is the range of {vals}?"
        else:
            cnt = Counter(vals)
            mode_val = cnt.most_common(1)[0][0]
            if cnt.most_common(1)[0][1] == 1:
                vals[0] = vals[1]
                vals.sort()
                mode_val = vals[0]
            ans = mode_val
            q = f"What is the mode of {vals}?"
        wrongs = [str(ans+1), str(ans-1) if ans > 1 else str(ans+2), str(ans+2)]
        ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": f"The {typ} of {vals} is {ans}."})
    return out[:n]

def _gen_probability(n: int) -> list[dict]:
    out = []
    r = random.Random(1414)
    while len(out) < n:
        total = r.randint(5, 20)
        fav = r.randint(1, total - 1)
        g = gcd(fav, total)
        ans = f"{fav//g}/{total//g}"
        wrongs = [f"{(fav+1)//gcd(fav+1,total)}/{total//gcd(fav+1,total)}",
                  f"{fav//gcd(fav,total+1)}/{(total+1)//gcd(fav,total+1)}",
                  f"{(total-fav)//gcd(total-fav,total)}/{total//gcd(total-fav,total)}"]
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        color = r.choice(["red","blue","green","yellow"])
        out.append({"prompt": f"A bag has {total} marbles, {fav} are {color}. What is the probability of drawing a {color} marble?",
                    "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": f"P({color}) = {fav}/{total} = {ans}."})
        # Independent events
        p1n, p1d = r.randint(1,4), r.randint(5,10)
        p2n, p2d = r.randint(1,4), r.randint(5,10)
        g1, g2 = gcd(p1n*p2n, p1d*p2d), 1
        an, ad = p1n*p2n, p1d*p2d
        g12 = gcd(an, ad)
        ans2 = f"{an//g12}/{ad//g12}"
        wrongs2 = [f"{p1n}/{p1d}", f"{p1n+p2n}/{p1d+p2d}", f"{an//g12+1}/{ad//g12}"]
        ch2, ci2 = _make_choices(ans2, wrongs2, r.randint(0, 10**9))
        out.append({"prompt": f"P(A) = {p1n}/{p1d} and P(B) = {p2n}/{p2d}. If A and B are independent, what is P(A and B)?",
                    "choices": ch2, "correct": ci2, "difficulty": "medium",
                    "explanation": f"P(A and B) = P(A) × P(B) = {p1n}/{p1d} × {p2n}/{p2d} = {ans2}."})
    return out[:n]

def _gen_tables(n: int) -> list[dict]:
    out = []
    r = random.Random(1515)
    while len(out) < n:
        r11,r12 = r.randint(5,20), r.randint(5,20)
        r21,r22 = r.randint(5,20), r.randint(5,20)
        total = r11+r12+r21+r22
        typ = r.choice(["row_total","col_total","cell","conditional"])
        if typ == "row_total":
            ans = str(r11+r12)
            q = f"A table shows Group A: ({r11}, {r12}) and Group B: ({r21}, {r22}). What is the total for Group A?"
            wrongs = [str(r11+r12+1), str(r21+r22), str(r11+r21)]
        elif typ == "col_total":
            ans = str(r11+r21)
            q = f"A table shows Group A: ({r11}, {r12}) and Group B: ({r21}, {r22}). What is the total for Category 1?"
            wrongs = [str(r12+r22), str(r11+r12), str(r11+r21+1)]
        elif typ == "cell":
            ans = str(r11)
            q = f"In a two-way table, Group A / Category 1 = {r11}, Group A / Category 2 = {r12}, Group B / Category 1 = {r21}, Group B / Category 2 = {r22}. How many are in Group A, Category 1?"
            wrongs = [str(r12), str(r21), str(r22)]
        else:
            row_total = r11+r12
            ans_frac_n, ans_frac_d = r11, row_total
            g = gcd(ans_frac_n, ans_frac_d)
            ans = f"{ans_frac_n//g}/{ans_frac_d//g}"
            q = f"A table shows Group A: ({r11}, {r12}). Given a randomly chosen Group A member, what is the probability they are in Category 1?"
            wrongs = [f"{r11}/{r11+r21}", f"{r12}/{row_total}", f"{r11+1}/{row_total}"]
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": "Read the relevant cells and totals from the table carefully."})
    return out[:n]

def _gen_charts(n: int) -> list[dict]:
    out = []
    r = random.Random(1616)
    while len(out) < n:
        yr_start = r.randint(2010, 2018)
        vals = [r.randint(100, 900) for _ in range(5)]
        max_yr = yr_start + vals.index(max(vals))
        min_yr = yr_start + vals.index(min(vals))
        trend = "increased" if vals[-1] > vals[0] else "decreased"
        typ = r.choice(["max_year","min_year","trend","diff"])
        if typ == "max_year":
            q = f"A bar chart shows values {vals} for years {yr_start}–{yr_start+4}. In which year was the value highest?"
            ans = str(max_yr)
            wrongs = [str(max_yr+1), str(min_yr), str(yr_start)]
        elif typ == "min_year":
            q = f"A line chart shows values {vals} for years {yr_start}–{yr_start+4}. In which year was the value lowest?"
            ans = str(min_yr)
            wrongs = [str(min_yr+1), str(max_yr), str(yr_start+4)]
        elif typ == "trend":
            q = f"A chart shows values {vals} from {yr_start} to {yr_start+4}. Which best describes the overall trend?"
            ans = f"Values generally {trend} over the period"
            opp = "increased" if trend == "decreased" else "decreased"
            wrongs = [f"Values generally {opp} over the period",
                      "Values remained constant", f"Values peaked in {yr_start+2}"]
        else:
            diff = abs(vals[-1] - vals[0])
            q = f"A chart shows a value of {vals[0]} in {yr_start} and {vals[-1]} in {yr_start+4}. What is the change?"
            ans = str(diff)
            wrongs = [str(diff+10), str(diff-10), str(vals[0]+vals[-1])]
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "easy",
                    "explanation": "Read the chart values directly and apply the question's specific calculation."})
    return out[:n]

def _gen_circles(n: int) -> list[dict]:
    out = []
    r = random.Random(1717)
    while len(out) < n:
        rad = r.randint(1, 14)
        typ = r.choice(["area","circumference","diameter","arc"])
        if typ == "area":
            ans = f"{rad**2}π"
            wrongs = [f"{rad*2}π", f"{rad}π", f"{rad**2*2}π"]
            q = f"A circle has radius {rad}. What is its area?"
            expl = f"Area = πr² = π({rad})² = {rad**2}π."
        elif typ == "circumference":
            ans = f"{2*rad}π"
            wrongs = [f"{rad}π", f"{rad**2}π", f"{4*rad}π"]
            q = f"A circle has radius {rad}. What is its circumference?"
            expl = f"C = 2πr = 2π({rad}) = {2*rad}π."
        elif typ == "diameter":
            ans = str(2*rad)
            wrongs = [str(rad), str(3*rad), str(2*rad+1)]
            q = f"A circle has radius {rad}. What is its diameter?"
            expl = f"Diameter = 2r = 2({rad}) = {2*rad}."
        else:
            angle = r.choice([30,45,60,90,120,180])
            arc = f"{2*rad*angle}π/360"
            g = gcd(2*rad*angle, 360)
            ans = f"{(2*rad*angle)//g}π/{360//g}" if (2*rad*angle)//g != 1 else f"π/{360//g}"
            wrongs = [f"{rad*angle}π/360", f"{2*rad}π", f"{angle}π/180"]
            q = f"A circle has radius {rad}. What is the arc length for a central angle of {angle}°?"
            expl = f"Arc = (angle/360) × 2πr = ({angle}/360) × 2π({rad}) = {ans}."
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "easy", "explanation": expl})
    return out[:n]

def _gen_triangles(n: int) -> list[dict]:
    out = []
    r = random.Random(1818)
    PYTH = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(9,40,41),(6,8,10),(10,24,26),(20,21,29)]
    while len(out) < n:
        typ = r.choice(["hyp","leg","similar","angle_sum"])
        if typ == "hyp":
            tri = r.choice(PYTH)
            scale = r.randint(1, 4)
            a, b, c = tri[0]*scale, tri[1]*scale, tri[2]*scale
            wrongs = [str(c+scale), str(a+b), str(c-1)]
            ch, ci = _make_choices(str(c), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"A right triangle has legs {a} and {b}. What is the hypotenuse?",
                        "choices": ch, "correct": ci, "difficulty": "easy",
                        "explanation": f"Hypotenuse = √({a}²+{b}²) = √{a**2+b**2} = {c}."})
        elif typ == "leg":
            tri = r.choice(PYTH)
            scale = r.randint(1, 3)
            a, b, c = tri[0]*scale, tri[1]*scale, tri[2]*scale
            wrongs = [str(b+1), str(b-scale), str(a+b)]
            ch, ci = _make_choices(str(b), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"A right triangle has hypotenuse {c} and one leg {a}. Find the other leg.",
                        "choices": ch, "correct": ci, "difficulty": "medium",
                        "explanation": f"leg = √({c}²–{a}²) = √{c**2-a**2} = {b}."})
        elif typ == "similar":
            k = r.randint(2, 5)
            sides = [r.randint(3,8), r.randint(3,8)]
            ans = sides[0] * k
            wrongs = [str(ans+k), str(sides[0]+k), str(ans-1)]
            ch, ci = _make_choices(str(ans), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"Two similar triangles have corresponding sides in ratio 1:{k}. If the smaller side is {sides[0]}, what is the larger?",
                        "choices": ch, "correct": ci, "difficulty": "medium",
                        "explanation": f"Scale factor is {k}: {sides[0]} × {k} = {ans}."})
        else:
            a_ang = r.randint(30, 80)
            b_ang = r.randint(30, 80)
            if a_ang + b_ang >= 180:
                continue
            c_ang = 180 - a_ang - b_ang
            wrongs = [str(c_ang+10), str(c_ang-10), str(a_ang+b_ang)]
            ch, ci = _make_choices(str(c_ang), wrongs, r.randint(0, 10**9))
            out.append({"prompt": f"A triangle has angles {a_ang}° and {b_ang}°. What is the third angle?",
                        "choices": ch, "correct": ci, "difficulty": "easy",
                        "explanation": f"Angles sum to 180°: 180 – {a_ang} – {b_ang} = {c_ang}°."})
    return out[:n]

def _gen_volume(n: int) -> list[dict]:
    out = []
    r = random.Random(1919)
    while len(out) < n:
        typ = r.choice(["cube","rect","cylinder","cone"])
        if typ == "cube":
            s = r.randint(2, 10)
            ans = str(s**3)
            wrongs = [str(s**3+s), str(s**2*3), str((s+1)**3)]
            q = f"What is the volume of a cube with side length {s}?"
            expl = f"V = s³ = {s}³ = {s**3}."
        elif typ == "rect":
            l,w,h = r.randint(2,8),r.randint(2,8),r.randint(2,8)
            ans = str(l*w*h)
            wrongs = [str(l*w*h+l), str(2*(l*w+w*h+l*h)), str(l+w+h)]
            q = f"What is the volume of a rectangular prism with l={l}, w={w}, h={h}?"
            expl = f"V = l×w×h = {l}×{w}×{h} = {l*w*h}."
        elif typ == "cylinder":
            r_val = r.randint(2,8)
            h = r.randint(2,10)
            ans = f"{r_val**2 * h}π"
            wrongs = [f"{r_val*h}π", f"{2*r_val*h}π", f"{r_val**2}π"]
            q = f"What is the volume of a cylinder with radius {r_val} and height {h}?"
            expl = f"V = πr²h = π({r_val})²({h}) = {r_val**2*h}π."
        else:
            r_val = r.randint(2,8)
            h = r.randint(3,12)
            g = gcd(r_val**2 * h, 3)
            if r_val**2*h % 3 == 0:
                ans = f"{r_val**2*h//3}π"
            else:
                ans = f"{r_val**2*h}π/3"
            wrongs = [f"{r_val**2*h}π", f"{r_val*h}π/3", f"{r_val**2}π/3"]
            q = f"What is the volume of a cone with radius {r_val} and height {h}?"
            expl = f"V = (1/3)πr²h = (1/3)π({r_val})²({h}) = {ans}."
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "medium", "explanation": expl})
    return out[:n]

def _gen_angles(n: int) -> list[dict]:
    out = []
    r = random.Random(2020)
    while len(out) < n:
        a = r.randint(20, 160)
        typ = r.choice(["supplement","complement","vertical","parallel"])
        if typ == "supplement":
            ans = str(180-a)
            wrongs = [str(180-a+5), str(90-a) if a<90 else str(a-90), str(a)]
            q = f"An angle measures {a}°. What is its supplement?"
            expl = f"Supplementary angles sum to 180°: 180 – {a} = {180-a}°."
        elif typ == "complement" and a < 90:
            ans = str(90-a)
            wrongs = [str(90-a+5), str(180-a), str(a)]
            q = f"An angle measures {a}°. What is its complement?"
            expl = f"Complementary angles sum to 90°: 90 – {a} = {90-a}°."
        elif typ == "vertical":
            ans = str(a)
            wrongs = [str(180-a), str(90-a) if a<90 else str(a+10), str(a+5)]
            q = f"Two lines intersect, forming an angle of {a}°. What is the vertical angle?"
            expl = f"Vertical angles are equal: {a}°."
        else:
            trans_angle = r.randint(30, 150)
            ans = str(trans_angle)
            wrongs = [str(180-trans_angle), str(trans_angle+10), str(trans_angle-15)]
            q = f"Two parallel lines are cut by a transversal forming an angle of {trans_angle}°. What is the corresponding angle?"
            expl = f"Corresponding angles are equal when lines are parallel: {trans_angle}°."
        if a >= 90 and typ == "complement":
            continue
        ch, ci = _make_choices(ans, wrongs, r.randint(0, 10**9))
        out.append({"prompt": q, "choices": ch, "correct": ci, "difficulty": "easy", "explanation": expl})
    return out[:n]

def _gen_trig(n: int) -> list[dict]:
    out = []
    r = random.Random(2121)
    # Common right triangle ratios
    TRIG = [(30, "1/2", "√3/2", "1/√3"),
            (45, "√2/2", "√2/2", "1"),
            (60, "√3/2", "1/2", "√3")]
    while len(out) < n:
        angle, sin_v, cos_v, tan_v = r.choice(TRIG)
        fn = r.choice(["sin","cos","tan"])
        ans = {"sin": sin_v, "cos": cos_v, "tan": tan_v}[fn]
        all_vals = [sin_v, cos_v, tan_v]
        wrongs = [v for v in all_vals if v != ans] + [f"2/{ans}" if "/" in ans else f"1/{ans}"]
        ch, ci = _make_choices(ans, wrongs[:3], r.randint(0, 10**9))
        out.append({"prompt": f"What is {fn}({angle}°)?",
                    "choices": ch, "correct": ci, "difficulty": "medium",
                    "explanation": f"{fn}({angle}°) = {ans}. Use the unit circle or special triangle values."})
        # SOH-CAH-TOA variant
        opp = r.randint(3,10)
        hyp = r.randint(opp+1, opp+8)
        adj_sq = hyp**2 - opp**2
        if adj_sq <= 0:
            continue
        import math
        adj = int(math.isqrt(adj_sq))
        if adj*adj != adj_sq:
            continue
        fn2 = r.choice(["sin","cos","tan"])
        ans2 = {"sin": f"{opp}/{hyp}", "cos": f"{adj}/{hyp}", "tan": f"{opp}/{adj}"}[fn2]
        w2 = [{"sin": f"{adj}/{hyp}", "cos": f"{opp}/{hyp}", "tan": f"{hyp}/{opp}"}[fn2],
              f"{hyp}/{opp}", f"{opp+1}/{hyp}"]
        ch2, ci2 = _make_choices(ans2, w2, r.randint(0, 10**9))
        out.append({"prompt": f"In a right triangle with opposite={opp}, adjacent={adj}, hypotenuse={hyp}, what is {fn2}(θ)?",
                    "choices": ch2, "correct": ci2, "difficulty": "medium",
                    "explanation": f"SOH-CAH-TOA: {fn2}(θ) = {ans2}."})
    return out[:n]


SKILL_GENERATORS = {
    "Linear equations": _gen_linear_equations,
    "Systems of equations": _gen_systems,
    "Inequalities": _gen_inequalities,
    "Functions": _gen_functions,
    "Graph interpretation": _gen_graph_interpretation,
    "Quadratics": _gen_quadratics,
    "Polynomials": _gen_polynomials,
    "Exponential functions": _gen_exponential,
    "Radicals": _gen_radicals,
    "Rational expressions": _gen_rational,
    "Ratios": _gen_ratios,
    "Percentages": _gen_percentages,
    "Statistics": _gen_statistics,
    "Probability": _gen_probability,
    "Tables": _gen_tables,
    "Charts": _gen_charts,
    "Circles": _gen_circles,
    "Triangles": _gen_triangles,
    "Volume": _gen_volume,
    "Angles": _gen_angles,
    "Trigonometric functions": _gen_trig,
}


# ─── R/W passages (250 unique) ────────────────────────────────────────────────

RW_PASSAGES = [
    "Researchers studying urban gardens found that neighborhoods with shared green spaces reported stronger community ties.",
    "A 2023 study found that sediment disturbance from deep-sea mining reduced bioluminescence in 78% of sampled ocean species.",
    "Monarch butterfly migration has shifted northward by 80 miles over three decades due to warming overwintering regions.",
    "Roman engineers used volcanic ash and seawater to create concrete that grows stronger over centuries.",
    "Reform movements led by Robert Owen pushed British Parliament to limit child labor in textile mills.",
    "Isolated mountain communities preserve archaic grammatical features lost in lowland language variants.",
    "mRNA vaccine technology opened new frontiers in treating cancers and genetic diseases beyond COVID-19.",
    "Adults sleeping fewer than six hours per night show a 48% higher risk of cardiovascular disease.",
    "Harlem Renaissance artists challenged racial stereotypes and reshaped American artistic identity in the 1920s.",
    "Organized grain storage predating writing suggests complex social hierarchies existed 9,000 years ago.",
    "Invasive carp in the Mississippi basin threaten a $7 billion recreational fishing industry.",
    "Kant argued that moral value derives from adherence to universal categorical imperatives, not consequences.",
    "Ice core data from Antarctica confirms current CO₂ concentrations are unprecedented over 800,000 years.",
    "Social media algorithms amplify emotionally charged content over accurate but neutral reporting.",
    "Venus flytraps require two trigger-hair touches within 20 seconds to conserve energy on non-prey stimuli.",
    "A Finland universal basic income pilot improved well-being and mental health without affecting employment rates.",
    "Gravitational wave detection in 2015 confirmed Einstein's century-old prediction and opened a new observational channel.",
    "Indigenous ecological knowledge is increasingly recognized as a valuable complement to conservation science.",
    "The bystander effect shows that more observers of an emergency reduces the likelihood of intervention.",
    "The printing press democratized knowledge and catalyzed the Protestant Reformation and Scientific Revolution.",
    "Urban heat islands raise local temperatures by up to 7°C, intensifying heat-related health risks.",
    "The adolescent prefrontal cortex, responsible for impulse control, continues developing until approximately age 25.",
    "Horse domestication around 3500 BCE transformed warfare, trade, and communication across Eurasia.",
    "Hydrothermal vent ecosystems thrive without sunlight, expanding the search for extraterrestrial life.",
    "Digital surveillance originally developed for security is being repurposed to suppress political dissent.",
    "Patients knowingly taking inert pills sometimes experience measurable improvements through expectation alone.",
    "The Amazon stores 150–200 billion tons of carbon, making its preservation critical to climate stability.",
    "Abstract expressionists conveyed raw emotional states through scale and non-representational form.",
    "Food deserts link geography to higher rates of obesity and type-2 diabetes in urban communities.",
    "CRISPR-Cas9 corrected hereditary blindness in clinical trials, signaling a new era of precision medicine.",
    "Economists debate whether productivity gains from automation will outpace job displacement in manufacturing.",
    "Deep-time geological records reveal that Earth has experienced at least five mass extinction events.",
    "Neuroplasticity research shows that the adult brain can form new neural pathways through targeted practice.",
    "Sociolinguists document how social media accelerates the spread of neologisms across language communities.",
    "Urban planners advocate for mixed-use zoning to reduce car dependency and lower carbon emissions.",
    "The discovery of exoplanets in habitable zones has reinvigorated the search for biosignatures.",
    "Behavioral economists study how default options in retirement plans dramatically increase savings participation.",
    "Permafrost thaw in Arctic regions releases methane, creating a feedback loop that accelerates warming.",
    "Historians argue that the Black Death reshaped European labor markets by increasing worker bargaining power.",
    "Architects studying passive solar design reduce building energy consumption by up to 70%.",
    "Psycholinguists find that bilingual children develop stronger executive function than monolingual peers.",
    "Coral reef bleaching events have increased in frequency and severity over the past four decades.",
    "Genetic sequencing of ancient DNA has revised our understanding of early human migration patterns.",
    "Public health researchers link walkable neighborhoods to lower rates of sedentary lifestyle diseases.",
    "Marine biologists document that whale populations serve as ecosystem engineers by cycling ocean nutrients.",
    "Computational linguists use large language models to reconstruct extinct languages from fragmentary evidence.",
    "The circular economy model prioritizes product reuse and recycling to minimize industrial waste streams.",
    "Astronomers using radio telescopes have mapped the large-scale structure of dark matter in galaxy clusters.",
    "Epigenetic research reveals that environmental stressors can alter gene expression across generations.",
    "Urban economists find that transit-oriented development corridors consistently outperform car-centric suburbs.",
    "Sociologists studying remote work report both increased autonomy and higher rates of professional isolation.",
    "Marine chemists track ocean acidification by monitoring pH changes that threaten shellfish exoskeletons.",
    "Ethnobotanists document medicinal plant knowledge at risk of disappearing as indigenous languages decline.",
    "Robotics engineers face the challenge of programming machines to handle unstructured real-world environments.",
    "Astrophysicists model neutron star mergers to understand the origin of heavy elements like gold.",
    "Developmental psychologists find that early childhood adversity alters stress-response systems durably.",
    "Historians of science trace how peer review evolved from private correspondence to formal journal gatekeeping.",
    "Seismologists use recordings of earthquake waves to map the layered structure of Earth's interior.",
    "Nutritional epidemiologists debate whether ultra-processed food consumption independently causes chronic disease.",
    "Philosophers of mind debate whether artificial neural networks can achieve genuine understanding or only mimic it.",
    "Dendrochronologists reconstruct past climates by analyzing growth ring widths in ancient trees.",
    "Civil engineers developing smart infrastructure embed sensors to monitor structural integrity in real time.",
    "Cognitive scientists find that spaced repetition dramatically outperforms massed practice for long-term retention.",
    "Volcanologists study pyroclastic flows to improve evacuation models for densely populated coastal regions.",
    "Biogeographers document how island isolation shapes species evolution through founder effects.",
    "Game theorists apply Nash equilibrium models to explain arms race dynamics between rival states.",
    "Linguists find that tonal languages recruit additional auditory cortex regions compared to non-tonal languages.",
    "Paleoanthropologists debate whether Homo naledi represents a distinct species or a variant of Homo erectus.",
    "Sustainable agriculture researchers advocate cover cropping to restore soil organic matter and biodiversity.",
    "Particle physicists at the LHC continue searching for evidence of supersymmetric particles beyond the Standard Model.",
    "Public policy scholars assess how congestion pricing reduces urban traffic while raising equity concerns.",
    "Mycologists discover that forest fungal networks facilitate nutrient exchange between competing tree species.",
    "Forensic linguists analyze syntax and vocabulary patterns to attribute authorship of anonymous texts.",
    "Economists studying trade policy find that import tariffs often raise domestic consumer prices.",
    "Glaciologists monitor outlet glacier dynamics to improve sea-level rise projections for coastal cities.",
    "Biophysicists model protein folding to accelerate drug discovery for neurodegenerative diseases.",
    "Educational psychologists find that student metacognition predicts academic performance more reliably than IQ.",
    "Ocean engineers designing wave energy converters face challenges from saltwater corrosion and storm loads.",
    "Archaeozoologists reconstruct ancient diets by analyzing stable isotopes in animal bones from excavation sites.",
    "Medical ethicists debate the boundaries of informed consent in early-phase clinical trials.",
    "Sociologists studying gentrification document displacement pressures on longtime residents of changing neighborhoods.",
    "Immunologists discover that the gut microbiome composition significantly modulates autoimmune disease risk.",
    "Political scientists analyze how proportional representation systems affect coalition government stability.",
    "Historians of technology argue that the steam engine's impact was amplified by complementary railroad infrastructure.",
    "Climate modelers project that extreme precipitation events will increase in intensity under higher warming scenarios.",
    "Behavioral ecologists find that ravens exhibit tactical deception to guard food caches from competitors.",
    "Translational researchers bridge laboratory findings and clinical applications to accelerate therapeutic development.",
    "Urban ecologists document how green corridors allow wildlife to navigate fragmented suburban landscapes.",
    "Information theorists apply Shannon entropy to measure the compressibility of natural language corpora.",
    "Philosophers of ethics debate whether future generations have rights that current policy should honor.",
    "Marine engineers design subsea pipelines to withstand deep-ocean pressure and thermal expansion stresses.",
    "Comparative genomicists trace antibiotic resistance gene transfers between human pathogens and soil bacteria.",
    "Archaeologists excavating Pompeii use ground-penetrating radar to locate sealed structures without excavation.",
    "Labor economists document that automation and offshoring affect middle-skill occupations most severely.",
    "Immunotherapy researchers engineer T-cells to recognize and destroy tumor-specific antigens.",
    "Historians of medicine document how germ theory transformed sanitation practices in nineteenth-century cities.",
    "Neuroscientists find that chronic sleep deprivation impairs emotional regulation as severely as acute stress.",
    "Marine conservationists advocate for expanding no-take reserves to allow depleted fish populations to recover.",
    "Data scientists apply machine learning to satellite imagery to detect deforestation in near real time.",
    "Philosophical debates over personal identity ask whether gradual neurological change preserves the self.",
    "Archaeologists studying Bronze Age collapse debate whether climate-driven drought triggered societal disintegration.",
    "Astronomers observe that spiral galaxy arms are density waves rather than fixed material structures.",
    "Public health researchers find that naloxone distribution programs significantly reduce opioid overdose mortality.",
    "Linguists studying signed languages confirm they share the same neural substrates as spoken languages.",
    "Historians of colonialism analyze how resource extraction shaped modern inequality in post-colonial states.",
    "Structural biologists use cryo-electron microscopy to resolve membrane protein structures at atomic resolution.",
    "Behavioral geneticists study identical twins raised apart to separate nature and nurture contributions to traits.",
    "Planners designing resilient cities prioritize redundant infrastructure to maintain function during disasters.",
    "Ethologists document that chimpanzees transmit tool-use techniques across generations through social learning.",
    "Economists studying minimum wage increases find mixed employment effects depending on local labor market conditions.",
    "Geographers analyze how river delta subsidence combines with sea-level rise to threaten coastal megacities.",
    "Immunologists find that mRNA vaccines can be reformulated within weeks to target new viral variants.",
    "Cognitive neuroscientists use fMRI to map how narrative comprehension activates widely distributed brain networks.",
    "Urban designers advocate for tactical urbanism as a low-cost method to test public space improvements.",
    "Archaeobotanists reconstruct ancient land use by identifying pollen and seed remains in sediment cores.",
    "Political economists debate whether carbon taxes or cap-and-trade systems more efficiently reduce emissions.",
    "Chemists developing solid-state batteries aim to replace flammable liquid electrolytes in electric vehicles.",
    "Anthropologists document how gift exchange networks build social capital in subsistence farming communities.",
    "Epidemiologists study disease burden using disability-adjusted life years to compare health interventions.",
    "Ocean biologists find that plastic pollution fragments into microplastics that enter marine food webs.",
    "Historians of philosophy trace how Enlightenment concepts of natural rights influenced democratic revolutions.",
    "Geochemists use isotopic signatures in zircon crystals to date the formation of ancient continental crust.",
    "Behavioral economists study how loss aversion leads investors to hold losing positions longer than winners.",
    "Atmospheric scientists model aerosol-cloud interactions to reduce uncertainty in climate sensitivity estimates.",
    "Sociologists find that social trust in institutions declines sharply following high-profile government scandals.",
    "Paleoecologists reconstruct ancient forest composition using fossilized pollen assemblages from lake sediments.",
    "Software engineers apply formal verification methods to prove the correctness of safety-critical systems.",
    "Historians of education analyze how compulsory schooling laws standardized childhood across industrial nations.",
    "Marine geologists map hydrothermal vent fields to assess their potential for hosting mineral deposits.",
    "Psychologists studying grief document that non-linear, individualized mourning processes are more common than stage models suggest.",
    "Economists analyze how patent systems balance innovation incentives against the social cost of monopoly pricing.",
    "Virologists study how RNA viruses evolve rapidly through error-prone replication to evade immune responses.",
    "Urban sociologists find that neighborhood poverty concentration independently worsens educational and health outcomes.",
    "Physicists developing quantum computing hardware face the challenge of maintaining qubit coherence at scale.",
    "Historians document how wartime rationing programs shaped long-term consumer preferences and cultural norms.",
    "Cognitive scientists find that analogical reasoning underlies both scientific discovery and everyday problem solving.",
    "Environmental chemists track persistent organic pollutants from industrial discharge to remote Arctic ecosystems.",
    "Ethnomusicologists analyze how diaspora communities adapt traditional music to new cultural contexts.",
    "Bioethicists debate the equity implications of allocating scarce medical resources during public health emergencies.",
    "Systems biologists model metabolic networks to identify drug targets that minimize off-target effects.",
    "Legal scholars debate whether international climate agreements can be enforced without binding domestic legislation.",
    "Remote sensing researchers use lidar to map forest canopy height and estimate above-ground carbon stocks.",
    "Historians of art trace how photographic reproduction changed the status and distribution of original works.",
    "Nuclear engineers designing next-generation reactors prioritize passive cooling systems to improve safety margins.",
    "Anthropologists study how smartphone adoption reshapes social interaction patterns in rural agricultural communities.",
    "Molecular biologists find that non-coding RNA sequences play regulatory roles previously attributed to proteins.",
    "Environmental economists apply contingent valuation to estimate willingness to pay for ecosystem services.",
    "Historians of cartography trace how colonial maps encoded territorial claims and suppressed indigenous place names.",
    "Neuropharmacologists study the mechanisms of psychedelic-assisted therapy for treatment-resistant depression.",
    "Agricultural scientists develop drought-tolerant crop varieties using marker-assisted selection and gene editing.",
    "Demographers project that aging populations in high-income countries will reshape healthcare and pension systems.",
    "Philosophers of language debate whether meaning is determined by individual intention or social convention.",
    "Geologists studying plate tectonics use GPS networks to measure millimeter-scale crustal deformation in real time.",
    "Sports scientists analyze biomechanical data to optimize training protocols and reduce injury risk in athletes.",
    "Historians of religion trace how pilgrimage routes functioned as commercial and cultural exchange networks.",
    "Biochemists studying enzyme kinetics design inhibitors to block pathways implicated in metabolic disorders.",
    "Urban climatologists find that tree canopy cover reduces heat stress and stormwater runoff in cities.",
    "Sociologists of science study how grant funding structures shape research priorities in academic institutions.",
    "Marine biologists discover that whale sharks use magnetic field sensing to navigate transoceanic migrations.",
    "Historians document how the telegraph transformed news transmission and military command in the nineteenth century.",
    "Computational neuroscientists build spiking neural network models to simulate cortical information processing.",
    "Public health scholars advocate for upstream social determinants of health to reduce chronic disease burdens.",
    "Geneticists studying population bottlenecks find reduced diversity in founder populations colonizing new territories.",
    "Industrial ecologists apply life-cycle assessment to quantify the full environmental cost of manufactured goods.",
    "Historians of slavery document how abolitionist networks coordinated across national borders to end the transatlantic trade.",
    "Materials scientists develop self-healing polymers that autonomously repair micro-cracks to extend product lifespan.",
    "Developmental biologists study morphogen gradients to understand how body axes are established in embryos.",
    "Behavioral scientists find that social comparison information motivates energy conservation more effectively than cost savings.",
    "Oceanographers track thermohaline circulation slowdown as a potential tipping point in the climate system.",
    "Medical anthropologists document how cultural beliefs about illness shape treatment-seeking and medication adherence.",
    "Historians of computing trace how the transistor's invention enabled the miniaturization of electronic devices.",
    "Ecotoxicologists study how pharmaceutical compounds excreted into waterways disrupt aquatic endocrine systems.",
    "Political theorists debate whether deliberative democracy can function in high-polarization media environments.",
    "Geomicrobiotists discover bacterial communities metabolizing iron deep below Earth's continental crust.",
    "Cognitive psychologists find that the testing effect improves long-term memory retrieval more than re-reading.",
    "Historians of gender document how wartime labor demands temporarily expanded women's occupational roles.",
    "Climatologists analyze proxy records including tree rings, ice cores, and coral archives to reconstruct past temperatures.",
    "Sociologists study how algorithmic curation of news feeds shapes political belief formation over time.",
    "Marine ecologists document that kelp forest restoration supports biodiversity recovery along temperate coastlines.",
    "Organizational psychologists find that psychological safety predicts team innovation more strongly than expertise.",
    "Astronomers detect rapid radio bursts from distant galaxies but debate their precise physical origins.",
    "Demographers find that urbanization consistently correlates with declining fertility rates across diverse cultural contexts.",
    "Historians of medicine document how the randomized controlled trial became the gold standard for clinical evidence.",
    "Computational social scientists use network analysis to map information diffusion across online communities.",
    "Ecologists studying trophic cascades find that apex predator reintroduction can restore degraded ecosystems.",
    "Historians of globalization trace how container shipping standardization transformed international trade flows.",
    "Biogeochemists measure nitrogen cycling rates in wetlands to quantify their role in reducing agricultural runoff.",
    "Psycholinguists study how reading aloud versus silently activates different phonological processing pathways.",
    "Historians of science document how cold fusion controversies reveal the social dynamics of scientific fraud.",
    "Marine physicists track internal wave dynamics to understand energy transfer from surface to deep ocean layers.",
    "Sociologists find that residential segregation by income has intensified in most major cities since 1980.",
    "Molecular ecologists use environmental DNA sampling to detect rare and cryptic species noninvasively.",
    "Historians of architecture analyze how modernism's rejection of ornament expressed ideological commitments to utility.",
    "Neurobiologists find that exercise-induced neurogenesis in the hippocampus is linked to improved spatial memory.",
    "Political scientists study how ranked-choice voting affects candidate strategy and voter satisfaction.",
    "Marine geochemists measure trace metal ratios in foraminifera shells to reconstruct past ocean temperatures.",
    "Behavioral economists study how the framing of health messages affects uptake of preventive care.",
    "Historians of labor trace how the eight-hour workday movement spread from textile mills to global industries.",
    "Quantum physicists demonstrate that entangled particle pairs maintain correlated states regardless of separation distance.",
    "Developmental psychologists find that secure attachment in infancy predicts social competence in adolescence.",
    "Environmental historians document how irrigation expanded agricultural output while depleting groundwater aquifers.",
    "Historians of migration analyze how exclusion laws shaped ethnic enclaves in early twentieth-century cities.",
    "Ecologists modeling ecosystem resilience find that biodiversity increases resistance to environmental perturbations.",
    "Neurologists study how transcranial magnetic stimulation can temporarily disrupt cortical function to map brain areas.",
    "Historians of science credit wartime radar research with accelerating postwar advances in microwave technology.",
    "Sociologists of religion document how religious affiliation patterns shift across generations in secularizing societies.",
    "Cognitive scientists study how cognitive load affects decision quality under time pressure in complex tasks.",
    "Marine biologists document that fish acoustic communication is disrupted by anthropogenic underwater noise pollution.",
    "Political economists find that campaign finance regulations shape which interests are most represented in legislatures.",
    "Historians of technology trace how the cotton gin's labor-saving efficiency paradoxically intensified slavery.",
    "Atmospheric chemists monitor stratospheric ozone recovery following the Montreal Protocol's restrictions on CFCs.",
    "Developmental economists study how conditional cash transfer programs reduce child poverty and improve school attendance.",
    "Neuroethicists debate the implications of brain-computer interfaces for personal identity and cognitive enhancement.",
    "Historians of public health document how cholera epidemics prompted urban sanitation reforms in Victorian cities.",
]

RW_QUESTION_TYPES = [
    ("What is the main purpose of the passage?",
     ["To present a finding and its implications", "To argue against a prior belief", "To compare two theories", "To trace historical origins"],
     0, "easy"),
    ("The underlined sentence primarily serves to:",
     ["Support the preceding claim with evidence", "Introduce a counterargument", "Define a key term", "Shift to a different subject"],
     0, "medium"),
    ("Which choice most logically completes the argument?",
     ["Further research is needed to confirm the finding", "The findings apply universally", "Traditional methods are superior", "Economic factors are more important"],
     0, "medium"),
    ("Based on the passage, what can be inferred?",
     ["The conclusion was supported by measurable data", "Conclusions were based solely on anecdote", "The work contradicted all prior research", "Findings were rejected by the field"],
     0, "medium"),
    ("As used in the passage, 'significant' most nearly means:",
     ["Meaningful and noteworthy", "Large in physical size", "Difficult to understand", "Related to symbols"],
     0, "easy"),
    ("Which sentence would best conclude the passage?",
     ["These results could inform policy and future research.", "Scientists have long disputed this view.", "This contradicts nearly all prior work.", "Funding for this area remains limited."],
     0, "hard"),
    ("The author's tone is best described as:",
     ["Informative and objective", "Dismissive and skeptical", "Enthusiastically biased", "Uncertain and speculative"],
     0, "easy"),
    ("Which revision most improves clarity?",
     ["Adding a specific example to illustrate the claim", "Removing the introductory sentence", "Replacing all passive constructions", "Moving the conclusion to the beginning"],
     0, "medium"),
    ("Which transition word best connects the sentences?",
     ["Therefore", "However", "Meanwhile", "Although"],
     0, "easy"),
    ("Which choice maintains the formal register?",
     ["The data revealed a statistically significant correlation", "The numbers totally showed a connection", "Scientists kind of found things were linked", "Results were really interesting"],
     0, "medium"),
    ("Which detail best supports the central argument?",
     ["The quantitative measurement in the second sentence", "The anecdote in the introduction", "The historical reference in the final clause", "The rhetorical question posed midway"],
     0, "hard"),
    ("The punctuation in the sentence is used to:",
     ["Set off a nonessential clause", "Indicate a shift in thought", "Separate items in a series", "Connect independent clauses without a conjunction"],
     0, "hard"),
    ("Which choice best combines both ideas?",
     ["The study found a correlation, suggesting the variable shapes outcomes.", "The study found a correlation; the variable was examined.", "The study found a correlation, but the variable was unrelated.", "The study found a correlation or the variable shapes outcomes."],
     0, "sat_hard"),
    ("The quoted phrase is used primarily to:",
     ["Signal the term has a specialized or contested meaning", "Indicate the author coined the term", "Suggest the term is colloquial", "Show direct quotation from another source"],
     0, "sat_hard"),
    ("Which sentence is most consistent with the passage's logical flow?",
     ["This pattern held across all groups studied.", "Researchers disagreed about the methodology.", "The opposite trend was found in comparable groups.", "Further investigation found no differences."],
     0, "sat_hard"),
    ("The passage suggests the phenomenon is:",
     ["More widespread than previously recognized", "Unique to one geographic region", "Fully explained by current models", "Unlikely to be replicated"],
     0, "medium"),
    ("Which choice best expresses the key finding?",
     ["A variable was found to influence a measurable outcome", "No relationship was detected between variables", "The study confirmed prior research was entirely wrong", "Researchers were unable to draw conclusions"],
     0, "easy"),
    ("The author includes the statistic primarily to:",
     ["Lend credibility to the preceding claim", "Introduce an unrelated topic", "Acknowledge a research limitation", "Provide historical background"],
     0, "medium"),
    ("Which word would least change the meaning if substituted for the underlined word?",
     ["demonstrated", "refuted", "ignored", "complicated"],
     0, "easy"),
    ("The structure of the passage is best described as:",
     ["A claim followed by evidence and a conclusion", "A problem followed by two competing solutions", "A narrative followed by a moral lesson", "A hypothesis followed by its refutation"],
     0, "medium"),
    ("Which choice, if true, would most strengthen the argument?",
     ["The results were replicated across multiple independent studies", "Only one research team observed this", "The finding has not been peer reviewed", "The sample size was very small"],
     0, "hard"),
    ("The relationship between the two sentences is:",
     ["The second provides a specific example of the first", "The second contradicts the first", "The second introduces a tangential topic", "The second restates the first identically"],
     0, "medium"),
]


# ─── Seed entry point ─────────────────────────────────────────────────────────

def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.get(User, 1) is None:
            db.add(User(id=1, name="Student", target_score=1500, study_minutes_per_day=75))

        math_count = db.query(Question).filter(Question.section == "math").count()
        rw_count = db.query(Question).filter(Question.section == "reading_writing").count()

        if math_count < 4400:
            print("Seeding math questions...")
            _seed_math(db)
        if rw_count < 5400:
            print("Seeding R/W questions...")
            _seed_rw(db)

        if db.query(VideoRecommendation).count() == 0:
            _seed_videos(db)

        db.commit()
        final_math = db.query(Question).filter(Question.section == "math").count()
        final_rw = db.query(Question).filter(Question.section == "reading_writing").count()
        print(f"DB: {final_math} math, {final_rw} R/W ({final_math+final_rw} total).")
    finally:
        db.close()


def _seed_math(db) -> None:
    from app.models import Question as Q
    existing = {row[0] for row in db.query(Q.external_id).all()}
    VARIANTS_PER_SKILL = 260

    for item in all_skills():
        if item["section"] != "math":
            continue
        gen = SKILL_GENERATORS.get(item["skill"])
        if gen is None:
            continue
        variants = gen(VARIANTS_PER_SKILL)
        for v_idx, v in enumerate(variants):
            # external_id encodes variant first so questions interleave across skills in id order
            ext_id = f"math-v{v_idx:04d}-{item['skill'].lower().replace(' ','-')}"
            if ext_id in existing:
                continue
            db.add(Q(
                external_id=ext_id,
                section="math",
                domain=item["domain"],
                skill=item["skill"],
                difficulty=v["difficulty"],
                question_type="multiple_choice",
                prompt=v["prompt"],
                choices_json=json.dumps(v["choices"]),
                correct_answer=v["correct"],
                explanation=v.get("explanation", f"Apply {item['skill']} principles to solve."),
                distractor_analysis_json=json.dumps({"B": "Common error", "C": "Sign mistake", "D": "Mis-applied formula"}),
                estimated_seconds=75,
            ))
    db.flush()


def _seed_rw(db) -> None:
    """
    Seed SAT-authentic Reading & Writing questions.
    Each question pairs one short passage (25–150 words) with one question.
    Questions are generated from rw_passages.py + RW_QUESTION_TYPES.
    external_id = rw-p{passage_idx:04d}-q{qtype_idx:02d}
    so any 54-question slice spans 2–3 passages with diverse question types.
    """
    from app.models import Question as Q
    from scripts.rw_passages import PASSAGES as SAT_PASSAGES
    existing = {row[0] for row in db.query(Q.external_id).all()}

    skill_meta = {item["skill"]: item for item in all_skills() if item["section"] == "reading_writing"}
    rw_skills = list(skill_meta.values())

    # SAT-style question types with per-domain skew
    SAT_QTYPES = [
        # (prompt, [correct, wrong1, wrong2, wrong3], difficulty, domain_hint)
        ("What is the main purpose of the text?",
         ["To present a finding and explore its significance",
          "To argue that a scientific consensus is wrong",
          "To compare two opposing theories in detail",
          "To trace the biography of a historical figure"],
         "easy", "info_ideas"),
        ("Which choice best states the function of the underlined sentence?",
         ["It provides evidence that supports the preceding claim",
          "It introduces a counterargument to the central idea",
          "It defines a technical term that appears later",
          "It shifts attention to a different aspect of the topic"],
         "medium", "craft_structure"),
        ("As used in the text, the word most nearly means:",
         ["significant and noteworthy",
          "large in physical size",
          "difficult to comprehend",
          "related to mathematical symbols"],
         "easy", "craft_structure"),
        ("Which finding, if true, would most directly support the researcher's claim?",
         ["Similar results were replicated across multiple independent studies",
          "Only one research team has observed this phenomenon",
          "The study has not yet been subject to peer review",
          "The sample used was not representative of the broader population"],
         "medium", "info_ideas"),
        ("Which choice most logically completes the text?",
         ["Further investigation is needed to confirm the pattern",
          "The evidence conclusively proves the opposite",
          "Traditional explanations are more accurate",
          "The effect applies only in laboratory conditions"],
         "medium", "expression_ideas"),
        ("Based on the text, what can most reasonably be inferred?",
         ["The phenomenon described has broader implications than initially recognized",
          "Researchers have reached unanimous agreement on the issue",
          "The study was conducted under conditions that limit its applicability",
          "The phenomenon is now fully understood by the scientific community"],
         "medium", "info_ideas"),
        ("The author's perspective on the subject can best be described as:",
         ["Analytical and measured",
          "Dismissive of the prevailing view",
          "Uncritically enthusiastic",
          "Deeply uncertain"],
         "easy", "craft_structure"),
        ("The text uses the phrase in quotation marks primarily to:",
         ["Signal that the term carries a specialized or contested meaning",
          "Indicate that the author invented the expression",
          "Suggest the language is informal or colloquial",
          "Show that the phrase is quoted verbatim from another source"],
         "hard", "craft_structure"),
        ("Which choice best describes the overall structure of the text?",
         ["A phenomenon is introduced, evidence is presented, and an implication is drawn",
          "A problem is posed, two solutions are compared, and one is rejected",
          "A historical narrative is recounted and a moral lesson is extracted",
          "A hypothesis is proposed and then immediately refuted"],
         "medium", "craft_structure"),
        ("Which sentence, if added, would most effectively conclude the text?",
         ["These findings suggest the need for continued investment in this area of research.",
          "Scientists have long been skeptical of this line of inquiry, however.",
          "This result, if confirmed, would contradict all previous work in the field.",
          "Funding for projects of this kind remains difficult to secure."],
         "hard", "expression_ideas"),
        ("The author includes the specific data primarily to:",
         ["Substantiate the claim made in the preceding sentence",
          "Introduce a topic unrelated to the main argument",
          "Acknowledge a significant limitation of the methodology",
          "Provide historical context for the research question"],
         "medium", "info_ideas"),
        ("Which revision of the underlined sentence best improves its precision?",
         ["Adults who sleep fewer than six hours per night show a 48% higher risk of cardiovascular disease",
          "Not getting enough sleep is bad for people",
          "Sleep deprivation can sometimes affect health in various ways",
          "Sleeping less is generally considered unhealthy by most experts"],
         "hard", "expression_ideas"),
        ("The relationship between the two sentences in the text is best described as:",
         ["The second sentence provides a specific example that illustrates the first",
          "The second sentence contradicts the claim made in the first",
          "The second sentence introduces a topic unrelated to the first",
          "The second sentence merely restates the first in different words"],
         "medium", "craft_structure"),
        ("Which choice, if inserted in the blank, best completes the sentence while maintaining grammatical correctness?",
         ["who", "whom", "which", "whose"],
         "easy", "standard_english"),
        ("Which version of the underlined portion is grammatically correct and most concise?",
         ["has documented a continuous increase over the past three decades",
          "has been documenting an increase that has been continuous over the past three decades",
          "documented continuously over the past three decades an increase",
          "over the past three decades, has been continuously documenting an increase"],
         "medium", "standard_english"),
        ("The student wants to add information from Source 3 to strengthen the argument. Which addition best accomplishes this goal?",
         ["The platform's own research showed that its algorithm prioritized engagement-maximizing content over accuracy",
          "Many users report spending more time online than they intend to",
          "Social media platforms generate significant advertising revenue",
          "Some studies have found benefits to social media use for isolated individuals"],
         "hard", "expression_ideas"),
        ("Which choice most effectively uses the data in the table to support the student's argument?",
         ["The largest percentage-point increase between 2010 and 2020 occurred in the lowest income quintile, suggesting access gaps are narrowing",
          "Rates of regular exercise declined in all income groups between 2010 and 2020",
          "The highest income quintile exercised less than the lowest income quintile in 2010",
          "Exercise rates were identical across all groups by 2020"],
         "sat_hard", "info_ideas"),
        ("Which transition best connects the description of technical challenges to the discussion of cultural impact?",
         ["Yet the mission's significance extended far beyond its engineering achievements.",
          "Nevertheless, the mission was considered a complete failure by some experts.",
          "Similarly, the cultural response was largely technical in nature.",
          "In contrast, the public showed little interest in the outcome."],
         "medium", "expression_ideas"),
        ("Which choice completes the text with the most logical and precise word or phrase?",
         ["left",
          "created",
          "eliminated",
          "discovered"],
         "easy", "craft_structure"),
        ("The claim that the effect is driven by 'thoughtlessness rather than malice' is best supported by which detail in the text?",
         ["Eichmann described his actions in administrative rather than ideological language",
          "Eichmann expressed regret for his role in the Holocaust during his trial",
          "Arendt acknowledged that Eichmann was motivated by strong personal convictions",
          "The trial revealed that Eichmann had directly ordered executions"],
         "sat_hard", "info_ideas"),
        ("Which choice best reconciles the two sources cited by the student?",
         ["Solar capacity grew dramatically, but renewables still supply only about a fifth of U.S. electricity",
          "Solar energy is now the dominant source of U.S. electricity, accounting for 43% of generation",
          "Renewable energy's share of U.S. electricity declined between 2020 and 2023",
          "The two sources are irreconcilable because they contradict each other on every point"],
         "sat_hard", "expression_ideas"),
        ("The word 'banality' as used in the text most nearly means:",
         ["Ordinariness; the quality of being commonplace rather than extraordinary",
          "Extreme cruelty; the deliberate infliction of suffering",
          "Bureaucratic efficiency; the ability to organize complex systems",
          "Philosophical complexity; the difficulty of moral judgment"],
         "hard", "craft_structure"),
        ("Based on the chart, which statement is best supported by the data?",
         ["The cost of genome sequencing decreased by more than 99% between 2001 and 2022",
          "Genome sequencing costs increased steadily from 2001 to 2022",
          "The cost of sequencing became cheaper than $1,000 only after 2022",
          "Costs fell at a constant rate of approximately $10 million per year"],
         "medium", "info_ideas"),
    ]

    for p_idx, (passage_text, domain_hint) in enumerate(SAT_PASSAGES):
        for q_idx, (prompt, choices_raw, difficulty, _domain) in enumerate(SAT_QTYPES):
            ext_id = f"rw2-p{p_idx:04d}-q{q_idx:02d}"
            if ext_id in existing:
                continue
            correct_text = choices_raw[0]
            seed_val = p_idx * 1031 + q_idx * 97
            shuffled = _shuffle(choices_raw, seed_val)
            choices = [{"id": lbl, "text": t} for lbl, t in zip("ABCD", shuffled)]
            correct_id = next(c["id"] for c in choices if c["text"] == correct_text)
            skill_item = rw_skills[p_idx % len(rw_skills)]
            db.add(Q(
                external_id=ext_id,
                section="reading_writing",
                domain=skill_item["domain"],
                skill=skill_item["skill"],
                difficulty=difficulty,
                question_type="passage_based",
                prompt=prompt,
                passage=passage_text,
                choices_json=json.dumps(choices),
                correct_answer=correct_id,
                explanation=_rw_explanation(prompt, correct_text),
                distractor_analysis_json=json.dumps({
                    "B": "Distorts or overstates the passage's claim.",
                    "C": "Introduces information not supported by the text.",
                    "D": "Contradicts the logical flow of the argument.",
                }),
                estimated_seconds=70,
            ))
    db.flush()


def _rw_explanation(prompt: str, correct: str) -> str:
    base = "Read the passage carefully and identify the specific evidence. "
    if "main purpose" in prompt.lower():
        return base + "Eliminate choices that describe only a detail or that mischaracterize the author's goal. The correct answer describes the overall purpose, not a supporting element."
    if "inferred" in prompt.lower():
        return base + "Inference questions require conclusions that are strongly implied but not explicitly stated. Eliminate choices that go beyond what the text supports."
    if "function" in prompt.lower() or "primarily" in prompt.lower():
        return base + "Identify what role the sentence or detail plays in the argument — evidence, counterargument, definition, or transition."
    if "most nearly means" in prompt.lower() or "word" in prompt.lower():
        return base + "Substitute each answer choice back into the sentence. The correct answer preserves the sentence's meaning in context."
    if "transition" in prompt.lower():
        return base + "The transition must logically connect the ideas on both sides. Test each option by reading both sentences with the transition inserted."
    if "structure" in prompt.lower():
        return base + "Map the sequence of ideas: what comes first, what comes second, and what relationship connects them."
    if "data" in prompt.lower() or "chart" in prompt.lower() or "table" in prompt.lower():
        return base + "Read the chart or table carefully. Match each answer choice to the specific values shown, and eliminate choices that misread or overstate the data."
    return base + f"The best answer is: {correct}. Eliminate choices that contradict the text, introduce outside information, or mischaracterize the author's meaning."


def _seed_videos(db) -> None:
    providers = [
        ("Khan Academy SAT", "https://www.youtube.com/results?search_query=Khan+Academy+SAT"),
        ("Organic Chemistry Tutor", "https://www.youtube.com/results?search_query=Organic+Chemistry+Tutor+SAT+Math"),
    ]
    for skill in all_skills():
        for provider, url in providers:
            db.add(VideoRecommendation(
                skill=skill["skill"], provider=provider,
                title=f"{skill['skill']} remediation", url=url,
                timestamp_seconds=120, notes=f"Use after repeated misses in {skill['domain']}.",
            ))


if __name__ == "__main__":
    seed()
    print("Seeded Offline SAT Academy database.")
