#--------------------------------------------------------------------
# Module        :   gal16v8
# Description   :   gal16v8 PLD implementation
# Caveats       :
# Author        :   Chris Alfred
# Copyright (c) Chris Alfred
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# Imports
#--------------------------------------------------------------------

# local
import macrocell

#--------------------------------------------------------------------
# Class
#--------------------------------------------------------------------

class Gal16v8:

    # according to the ATMEL Datasheet for ATF16V8B, ATF16V8BQ*, and ATF16V8BQL
    IO_COUNT = 18
    MACROCELL_COUNT = 8

    # Registered outputs always have eight product terms per output.
    # I/O's have seven product terms per output when local /OE is used, otherwise also eight.
    # The number will be dynamically adapted according to the config bits.
    MACROCELL_OR_TERMS = [
        8, 8, 8, 8, 8, 8, 8, 8
    ]
    FUSEROW_MAPPING = [
        # Pin name index    Name prefix
        (1,                 ''),
        (1,                 '!'),
        (0,                 ''),  # only in simple and complex mode, in registered mode this the global CLK
        (0,                 '!'), # only in simple and complex mode
        (2,                 ''),
        (2,                 '!'),
        (16,                ''),
        (16,                '!'),
        (3,                 ''),
        (3,                 '!'),
        (15,                ''),
        (15,                '!'),
        (4,                 ''),
        (4,                 '!'),
        (14,                ''),
        (14,                '!'),
        (5,                 ''),
        (5,                 '!'),
        (13,                ''),
        (13,                '!'),
        (6,                 ''),
        (6,                 '!'),
        (12,                ''),
        (12,                '!'),
        (7,                 ''),
        (7,                 '!'),
        (11,                ''),
        (11,                '!'),
        (8,                 ''),
        (8,                 '!'),
        (9,                 ''),  # only in simple and complex mode, in registered mode this is the global /OE
        (9,                 '!'), # only in simple and complex mode
    ]

    # simple     mode: SYN=1, AC-0=0, 8 product terms, no /OE
    # complex    mode: SYN=1, AC-0=1, 7 product terms + local /OE
    # registered mode: SYN=0, AC-0=1, Combinatorical outputs: 7 product terms + local /OE 
    #                                 Registered outputs: 8 product terms, global /OE
    #                                 Pin 1 and Pin 11 are permanently configured as CLK and /OE for registered outputs
    fuse_syn = 2192 # global
    fuse_ac0 = 2193 # global
    fuse_xor = 2048 # XOR fuses  = 2048..2055 for pin 19..11  '0' means active-low-output, '1' means active-high-output
    fuse_ac1 = 2120 # AC-1 fuses = 2120..2127 for pin 19..11  '0' means D-FlipFlop, '1' means combinatorical
    fuse_ues = 2056 # UES: fuse  = 2056..2119 for byte 7..0, MSB first

    #----------------------------------------------------------------
    # Private
    #----------------------------------------------------------------

    def _build_macrocells(self, fuse_data):

        self.macrocells = []

        if fuse_data[self.fuse_syn] != '0' and fuse_data[self.fuse_ac0] == '0':
          self.mode = 'simple'
          self.device_name = 'g16v8as'
        elif fuse_data[self.fuse_syn] != '0' and fuse_data[self.fuse_ac0] != '0':
          self.mode = 'complex'
          self.device_name = 'g16v8ma'
        elif fuse_data[self.fuse_syn] == '0' and fuse_data[self.fuse_ac0] != '0':
          self.mode = 'registered'
          self.device_name = 'g16v8ms'
        else:
          # not allowed, let compiler decide
          # TODO: throw error
          self.mode = 'complex'
          self.device_name = 'g16v8a'

        #self.macrocells.append(macrocell.Macrocell('AR',1))  # not supported by GAL16V8

        for macrocell_index in range(self.MACROCELL_COUNT):

            # Assume simple name
            pin_name = self.pin_names[(self.IO_COUNT - 1) - macrocell_index]

            # Determine the macrocell output mode
            pin_prefix = '!'  if fuse_data[macrocell_index + self.fuse_xor] == '0' else ''

            pin_suffix = ''
            if fuse_data[macrocell_index + self.fuse_ac1] == '0':
              pin_suffix = '.d'
              if self.mode != 'registered':
                # TODO: throw error, combination not allowed
                pass

            termcnt = self.MACROCELL_OR_TERMS[macrocell_index]
            local_oe = False
            if self.mode == 'complex':
              local_oe = True
            elif self.mode == 'registered':
              local_oe = fuse_data[macrocell_index + self.fuse_ac1] != '0'
            else:
              pass

            if local_oe:
              self.macrocells.append(macrocell.Macrocell(pin_prefix + pin_name + '.oe', 1, True))
              termcnt -= 1
            self.macrocells.append(macrocell.Macrocell(pin_prefix + pin_name + pin_suffix, termcnt))

        #self.macrocells.append(macrocell.Macrocell('SP',1)) # not supported by GAL16V8


    #----------------------------------------------------------------
    # Public
    #----------------------------------------------------------------

    def __init__(self, pin_names):

        self.device_name = 'p16v8' # will be overwritten in _build_macrocells
        mode = ''

        # Assign the pin names
        if len(pin_names) != self.IO_COUNT:
            raise ValueError('Incorrect number of pins')
        self.pin_names = pin_names

        # Assign fuse row
        self.fuserow = []
        for column in self.FUSEROW_MAPPING:
            self.fuserow.append( column[1] + self.pin_names[ column[0] ] )

    def print_terms(self, fuse_data):

        """
        Print logic terms
        fuse_data: array of fuses as '0' or '1'
        """

        # Build the macrocells
        self._build_macrocells(fuse_data)

        # Get the device fuse row
        number_of_and_terms = len(self.fuserow)

        # Loop over the macrocells
        fuse_index = 0
        for mc in self.macrocells:

            mc_equation = ''

            # Loop over the number of OR terms
            for or_term in range(mc.number_of_or_terms):

                # Get the AND fuse data for this OR term
                data = fuse_data[fuse_index:fuse_index+number_of_and_terms]

                # Initialise output line for this data
                s = ''

                # Loop over the OR fuses
                index = 0
                terms = 0
                prev_term = '0'
                for x in data:

                    # Two sequential terms X & !X with intact fuses will be 0
                    if index & 1 == 1:
                        if x == '0' and prev_term == '0':
                            s = "'b'0"
                            break

                    # Include non-fused terms
                    if x == '0': # '0' is NOT fused
                        if index != 0 and terms != 0:
                            s = s + ' & '
                        term_name = self.fuserow[index]

                        # Remove double NOTs
                        if term_name.startswith('!!'):
                            term_name = term_name[2:]

                        s = s + term_name
                        terms = terms + 1

                    prev_term = x
                    index = index + 1

                if terms == 0:
                    # If there are no terms the value is True ('1')
                    s = "'b'1"

                # Determine output target name
                output_name = mc.name
                if output_name.startswith('!!'):
                    output_name = output_name[2:]
                
                # Remove output inversion for OE signals
                if mc.oe and output_name.startswith('!'):
                    output_name = output_name[1:]

                if or_term == 0:
                    # The first line requires the output name
                    s = output_name + ' = ' + s
                    mc_equation = mc_equation + s + '\n'
                elif terms != 0 and s != "'b'0":
                    # Subsequent terms are ORed
                    s = ' ' * len(output_name) + ' # ' + s
                    mc_equation = mc_equation + s + '\n'

                fuse_index = fuse_index + number_of_and_terms

            mc_equation = mc_equation[:-1] + ';' + '\n'         
            print(mc_equation)
