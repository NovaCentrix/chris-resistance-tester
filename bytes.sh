#!/bin/bash
TEMPFILE=bytes_$$.dat
#create a hex dump listing of the file
fd2 $1 |
# extract just the hex values
cut -d ' ' -f 2-18 |
# make them one byte per line
sed 's/[ ]*$//' |
tr -cs '[:alnum:]' '\n' |
# calculate the distribution
sort | uniq -c |
cat > $TEMPFILE
join -1 2 -2 1 $TEMPFILE - <<cp1252_text_file
00	u+0000	NUL (null character)
01	u+0001	SOH (start of heading)
02	u+0002	STX (start of text)
03	u+0003	ETX (end of text)
04	u+0004	EOT (end of transmission)
05	u+0005	ENQ (enquiry)
06	u+0006	ACK (acknowledge)
07	u+0007	BEL (bell)
08	u+0008	BS  (backspace)
09	u+0009	HT  (horizontal tab)
0a	u+000a	LF  (new line)
0b	u+000b	VT  (vertical tab)
0c	u+000c	FF  (form feed)
0d	u+000d	CR  (carriage ret)
0e	u+000e	SO  (shift out)
0f	u+000f	SI  (shift in)
10	u+0010	DLE (data link escape)
11	u+0011	DC1 (device control 1)
12	u+0012	DC2 (device control 2)
13	u+0013	DC3 (device control 3)
14	u+0014	DC4 (device control 4)
15	u+0015	NAK (negative ack.)
16	u+0016	SYN (synchronous idle)
17	u+0017	ETB (end of trans. blk)
18	u+0018	CAN (cancel)
19	u+0019	EM  (end of medium)
1a	u+001a	SUB (substitute)
1b	u+001b	ESC (escape)
1c	u+001c	FS  (file separator)
1d	u+001d	GS  (group separator)
1e	u+001e	RS  (record separator)
1f	u+001f	US  (unit separator)
20	u+0020	space
21	u+0021	exclamation mark
22	u+0022	quotation mark
23	u+0023	number sign
24	u+0024	dollar sign
25	u+0025	percent sign
26	u+0026	ampersand
27	u+0027	apostrophe
28	u+0028	left parenthesis
29	u+0029	right parenthesis
2a	u+002a	asterisk
2b	u+002b	plus sign
2c	u+002c	comma
2d	u+002d	hyphen-minus
2e	u+002e	full stop
2f	u+002f	solidus
30	u+0030	digit zero
31	u+0031	digit one
32	u+0032	digit two
33	u+0033	digit three
34	u+0034	digit four
35	u+0035	digit five
36	u+0036	digit six
37	u+0037	digit seven
38	u+0038	digit eight
39	u+0039	digit nine
3a	u+003a	colon
3b	u+003b	semicolon
3c	u+003c	less-than sign
3d	u+003d	equals sign
3e	u+003e	greater-than sign
3f	u+003f	question mark
40	u+0040	commercial at
41	u+0041	latin capital letter a
42	u+0042	latin capital letter b
43	u+0043	latin capital letter c
44	u+0044	latin capital letter d
45	u+0045	latin capital letter e
46	u+0046	latin capital letter f
47	u+0047	latin capital letter g
48	u+0048	latin capital letter h
49	u+0049	latin capital letter i
4a	u+004a	latin capital letter j
4b	u+004b	latin capital letter k
4c	u+004c	latin capital letter l
4d	u+004d	latin capital letter m
4e	u+004e	latin capital letter n
4f	u+004f	latin capital letter o
50	u+0050	latin capital letter p
51	u+0051	latin capital letter q
52	u+0052	latin capital letter r
53	u+0053	latin capital letter s
54	u+0054	latin capital letter t
55	u+0055	latin capital letter u
56	u+0056	latin capital letter v
57	u+0057	latin capital letter w
58	u+0058	latin capital letter x
59	u+0059	latin capital letter y
5a	u+005a	latin capital letter z
5b	u+005b	left square bracket
5c	u+005c	reverse solidus
5d	u+005d	right square bracket
5e	u+005e	circumflex accent
5f	u+005f	low line
60	u+0060	grave accent
61	u+0061	latin small letter a
62	u+0062	latin small letter b
63	u+0063	latin small letter c
64	u+0064	latin small letter d
65	u+0065	latin small letter e
66	u+0066	latin small letter f
67	u+0067	latin small letter g
68	u+0068	latin small letter h
69	u+0069	latin small letter i
6a	u+006a	latin small letter j
6b	u+006b	latin small letter k
6c	u+006c	latin small letter l
6d	u+006d	latin small letter m
6e	u+006e	latin small letter n
6f	u+006f	latin small letter o
70	u+0070	latin small letter p
71	u+0071	latin small letter q
72	u+0072	latin small letter r
73	u+0073	latin small letter s
74	u+0074	latin small letter t
75	u+0075	latin small letter u
76	u+0076	latin small letter v
77	u+0077	latin small letter w
78	u+0078	latin small letter x
79	u+0079	latin small letter y
7a	u+007a	latin small letter z
7b	u+007b	left curly bracket
7c	u+007c	vertical line
7d	u+007d	right curly bracket
7e	u+007e	tilde
80	u+20ac	euro sign
82	u+201a	single low-9 quotation mark
83	u+0192	latin small letter f with hook
84	u+201e	double low-9 quotation mark
85	u+2026	horizontal ellipsis
86	u+2020	dagger
87	u+2021	double dagger
88	u+02c6	modifier letter circumflex accent
89	u+2030	per mille sign
8a	u+0160	latin capital letter s with caron
8b	u+2039	single left-pointing angle quotation mark
8c	u+0152	latin capital ligature oe
8e	u+017d	latin capital letter z with caron
91	u+2018	left single quotation mark
92	u+2019	right single quotation mark
93	u+201c	left double quotation mark
94	u+201d	right double quotation mark
95	u+2022	bullet
96	u+2013	en dash
97	u+2014	em dash
98	u+02dc	small tilde
99	u+2122	trade mark sign
9a	u+0161	latin small letter s with caron
9b	u+203a	single right-pointing angle quotation mark
9c	u+0153	latin small ligature oe
9e	u+017e	latin small letter z with caron
9f	u+0178	latin capital letter y with diaeresis
a0	u+00a0	no-break space
a1	u+00a1	inverted exclamation mark
a2	u+00a2	cent sign
a3	u+00a3	pound sign
a4	u+00a4	currency sign
a5	u+00a5	yen sign
a6	u+00a6	broken bar
a7	u+00a7	section sign
a8	u+00a8	diaeresis
a9	u+00a9	copyright sign
aa	u+00aa	feminine ordinal indicator
ab	u+00ab	left-pointing double angle quotation mark
ac	u+00ac	not sign
ad	u+00ad	soft hyphen
ae	u+00ae	registered sign
af	u+00af	macron
b0	u+00b0	degree sign
b1	u+00b1	plus-minus sign
b2	u+00b2	superscript two
b3	u+00b3	superscript three
b4	u+00b4	acute accent
b5	u+00b5	micro sign
b6	u+00b6	pilcrow sign
b7	u+00b7	middle dot
b8	u+00b8	cedilla
b9	u+00b9	superscript one
ba	u+00ba	masculine ordinal indicator
bb	u+00bb	right-pointing double angle quotation mark
bc	u+00bc	vulgar fraction one quarter
bd	u+00bd	vulgar fraction one half
be	u+00be	vulgar fraction three quarters
bf	u+00bf	inverted question mark
c0	u+00c0	latin capital letter a with grave
c1	u+00c1	latin capital letter a with acute
c2	u+00c2	latin capital letter a with circumflex
c3	u+00c3	latin capital letter a with tilde
c4	u+00c4	latin capital letter a with diaeresis
c5	u+00c5	latin capital letter a with ring above
c6	u+00c6	latin capital letter ae
c7	u+00c7	latin capital letter c with cedilla
c8	u+00c8	latin capital letter e with grave
c9	u+00c9	latin capital letter e with acute
ca	u+00ca	latin capital letter e with circumflex
cb	u+00cb	latin capital letter e with diaeresis
cc	u+00cc	latin capital letter i with grave
cd	u+00cd	latin capital letter i with acute
ce	u+00ce	latin capital letter i with circumflex
cf	u+00cf	latin capital letter i with diaeresis
d0	u+00d0	latin capital letter eth
d1	u+00d1	latin capital letter n with tilde
d2	u+00d2	latin capital letter o with grave
d3	u+00d3	latin capital letter o with acute
d4	u+00d4	latin capital letter o with circumflex
d5	u+00d5	latin capital letter o with tilde
d6	u+00d6	latin capital letter o with diaeresis
d7	u+00d7	multiplication sign
d8	u+00d8	latin capital letter o with stroke
d9	u+00d9	latin capital letter u with grave
da	u+00da	latin capital letter u with acute
db	u+00db	latin capital letter u with circumflex
dc	u+00dc	latin capital letter u with diaeresis
dd	u+00dd	latin capital letter y with acute
de	u+00de	latin capital letter thorn
df	u+00df	latin small letter sharp s
e0	u+00e0	latin small letter a with grave
e1	u+00e1	latin small letter a with acute
e2	u+00e2	latin small letter a with circumflex
e3	u+00e3	latin small letter a with tilde
e4	u+00e4	latin small letter a with diaeresis
e5	u+00e5	latin small letter a with ring above
e6	u+00e6	latin small letter ae
e7	u+00e7	latin small letter c with cedilla
e8	u+00e8	latin small letter e with grave
e9	u+00e9	latin small letter e with acute
ea	u+00ea	latin small letter e with circumflex
eb	u+00eb	latin small letter e with diaeresis
ec	u+00ec	latin small letter i with grave
ed	u+00ed	latin small letter i with acute
ee	u+00ee	latin small letter i with circumflex
ef	u+00ef	latin small letter i with diaeresis
f0	u+00f0	latin small letter eth
f1	u+00f1	latin small letter n with tilde
f2	u+00f2	latin small letter o with grave
f3	u+00f3	latin small letter o with acute
f4	u+00f4	latin small letter o with circumflex
f5	u+00f5	latin small letter o with tilde
f6	u+00f6	latin small letter o with diaeresis
f7	u+00f7	division sign
f8	u+00f8	latin small letter o with stroke
f9	u+00f9	latin small letter u with grave
fa	u+00fa	latin small letter u with acute
fb	u+00fb	latin small letter u with circumflex
fc	u+00fc	latin small letter u with diaeresis
fd	u+00fd	latin small letter y with acute
fe	u+00fe	latin small letter thorn
ff	u+00ff	latin small letter y with diaeresis
cp1252_text_file
