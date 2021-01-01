# PLDs

## G540 programmer

`ONLY WORKS IN XP`

`Set : Set Programming Operation Sequence, Remove Verify and Encrypt` These settings are lost every startup!!!!!!!

The G540 PAL programmer uses a non-standard .JED format.

### Read a PLD

Remeber: `Set : Set Programming Operation Sequence`

- Click `Read`
- `File : Save (S)`
- Select `JEDEC`
- Click `OK`

`The read file is ok, the saved file is wrong. You have to manually read the bits.`

### g540jedec

Convert CUPL compiler .JED to G540 compatible format.

Arguments:

- .JED from CUPL compiler
- Output file (.JED format for G540)

---

## CUPL Compiler

*ONLY WORKS IN XP*

Setup:

~~~
cuplsetup.bat
~~~

Compilation to .jed file:

~~~
cupl -j <.pld source file>
~~~

Conversion for G540 programmer (can be done in Windows 10):

~~~
python.exe g540jedec.py test.JED test_g540.JED
~~~

---


## GAL22V10 parsing

### gal22v10parse

Parse a .JED file and generate CUPL source file

Arguments:

- .JED source
- List of pin names separated by spaces in order of pins (skipping power pins 12,24). Prefix with `!` to indicate active low
- CUPL Name
- CUPL revision
- CUPL designer
- CUPL company name
- CUPL assembly
- CUPL location

Example:

~~~
python.exe .\gal22v10parse.py test_g540.JED "p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23" test 1 "Chris Alfred" "Company Name" myboard U6
~~~


## GAL16V8 parsing

### gal16v8parse

Parse a .JED file and generate CUPL source file

Arguments:

- .JED source
- List of pin names separated by spaces in order of pins (skipping power pins 10,20). Prefix with `!` to indicate active low
- CUPL Name
- CUPL revision
- CUPL designer
- CUPL company name
- CUPL assembly
- CUPL location

Examples:

~~~
python.exe .\gal16v8parse.py test_16v8.JED "p1 p2 p3 p4 p5 p6 p7 p8 p9 p11 p12 p13 p14 p15 p16 p17 p18 p19" test 1 "Chris Alfred" "Company Name" myboard U6

python.exe .\gal16v8parse.py GAL4_16v8-25.JED 'AS !RES A23 A22 A21 A20 A19 A18 !JP1_ROM !JP2_ROM CE_ROM_1MB !JP3_1MB_ROM p14 OVL_LOCAL !ADDR_MATCH p17 CE OVR' KupkeHddKick 1 "nobody" "Kupke" HddKick U4
~~~
