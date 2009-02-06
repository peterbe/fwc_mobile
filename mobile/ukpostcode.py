# Module     : postcode.py
# Synopsis   : UK postcode parser
# Programmer : Simon Brunning - simon@brunningonline.net
# Date       : 14 April 2004
# Version    : 1.0
# Copyright  : Released to the public domain. Provided as-is, with no warranty.
# Notes      :
'''UK postcode parser

Provides the parse_uk_postcode function for parsing UK postcodes.'''

import re

# Build up the regex patterns piece by piece
POSTAL_ZONES = ['AB', 'AL', 'B' , 'BA', 'BB', 'BD', 'BH', 'BL', 'BN', 'BR',
                'BS', 'BT', 'CA', 'CB', 'CF', 'CH', 'CM', 'CO', 'CR', 'CT',
                'CV', 'CW', 'DA', 'DD', 'DE', 'DG', 'DH', 'DL', 'DN', 'DT',
                'DY', 'E' , 'EC', 'EH', 'EN', 'EX', 'FK', 'FY', 'G' , 'GL',
                'GY', 'GU', 'HA', 'HD', 'HG', 'HP', 'HR', 'HS', 'HU', 'HX',
                'IG', 'IM', 'IP', 'IV', 'JE', 'KA', 'KT', 'KW', 'KY', 'L' ,
                'LA', 'LD', 'LE', 'LL', 'LN', 'LS', 'LU', 'M' , 'ME', 'MK',
                'ML', 'N' , 'NE', 'NG', 'NN', 'NP', 'NR', 'NW', 'OL', 'OX',
                'PA', 'PE', 'PH', 'PL', 'PO', 'PR', 'RG', 'RH', 'RM', 'S' ,
                'SA', 'SE', 'SG', 'SK', 'SL', 'SM', 'SN', 'SO', 'SP', 'SR',
                'SS', 'ST', 'SW', 'SY', 'TA', 'TD', 'TF', 'TN', 'TQ', 'TR',
                'TS', 'TW', 'UB', 'W' , 'WA', 'WC', 'WD', 'WF', 'WN', 'WR',
                'WS', 'WV', 'YO', 'ZE']
POSTAL_ZONES_ONE_CHAR = [zone for zone in POSTAL_ZONES if len(zone) == 1]
POSTAL_ZONES_TWO_CHARS = [zone for zone in POSTAL_ZONES if len(zone) == 2]
THIRD_POS_CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'S',
                   'T', 'U', 'W']
FOURTH_POS_CHARS = ['A', 'B', 'E', 'H', 'M', 'N', 'P', 'R', 'V', 'W', 'X',
                    'Y']
INCODE_CHARS = ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'J', 'L', 'N', 'P', 'Q',
                'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
OUTCODE_PATTERN = (r'(' + 
                   r'(?:(?:' +
                   '|'.join(POSTAL_ZONES_ONE_CHAR) +
                   r')(?:\d[' +
                   ''.join(THIRD_POS_CHARS) +
                   r']|\d{1,2}))' +
                   r'|' +
                   r'(?:(?:' +
                   '|'.join(POSTAL_ZONES_TWO_CHARS) +
                   r')(?:\d[' +
                   ''.join(FOURTH_POS_CHARS) +
                   r']|\d{1,2}))' +
                   r')')
INCODE_PATTERN = (r'(\d[' +
                  ''.join(INCODE_CHARS) +
                  r'][' +
                  ''.join(INCODE_CHARS) +
                  r'])')
POSTCODE_PATTERN = OUTCODE_PATTERN + INCODE_PATTERN
STANDALONE_OUTCODE_PATTERN = OUTCODE_PATTERN + r'\s*$'

# Compile regexs
POSTCODE_REGEX = re.compile(POSTCODE_PATTERN)
STANDALONE_OUTCODE_REGEX = re.compile(STANDALONE_OUTCODE_PATTERN)

def parse_uk_postcode(postcode, strict=True, incode_mandatory=True):
    '''Split UK postcode into outcode and incode portions.

    Arguments:
    postcode            The postcode to be split.
    strict              If true, the postcode will be validated according to
                        the rules as specified at the Universal Postal Union[1]
                        and The UK Government Data Standards Catalogue[2]. If
                        the supplied postcode doesn't adhere to these rules a
                        ValueError will be thrown.
    incode_mandatory    If true, and only an outcode has been supplied, the
                        function will throw a ValueError.

    Returns:            outcode, incode
                        
    Raises:             ValueError, if postcode is longer than seven
                        characters, or if 'strict' or 'incode_mandatory'
                        conditions are broken - see above.

    Usage example:      >>> from postcode import parse_uk_postcode
                        >>> parse_uk_postcode('cr0 2yr')
                        ('CR0', '2YR')
                        >>> parse_uk_postcode('cr0')
                        Traceback (most recent call last):
                          File "<interactive input>", line 1, in ?
                          File "postcode.py", line 101, in parse_uk_postcode
                            raise ValueError('Incode mandatory')
                        ValueError: Incode mandatory
                        >>> parse_uk_postcode('cr0', False, False)
                        ('CR0', '')
    
    [1] http://www.upu.int/post_code/en/countries/GBR.pdf
    [2] http://www.govtalk.gov.uk/gdsc/html/noframes/PostCode-2-1-Release.htm
    '''
    
    postcode = postcode.replace(' ', '').upper() # Normalize
    
    if len(postcode) > 7:
        raise ValueError('Incode mandatory')
    
    # Validate postcode
    if strict:
        
        # Try for full postcode match
        postcode_match = POSTCODE_REGEX.match(postcode)
        if postcode_match:
            return postcode_match.group(1, 2)
            
        # Try for outcode only match
        outcode_match = STANDALONE_OUTCODE_REGEX.match(postcode)
        if outcode_match:
            if incode_mandatory:
                raise ValueError('Incode mandatory')
            else:
                return outcode_match.group(1), ''

        # Try Girobank special case
        if postcode == 'GIR0AA':
            return 'GIR', '0AA'
        elif postcode == 'GIR':
            if incode_mandatory:
                raise ValueError('Incode mandatory')
            else:
                return 'GIR', ''
        
        # None of the above
        raise ValueError('Invalid postcode')
        
    # Just chop up whatever we've been given.
    else:
        # Outcode only
        if len(postcode) <= 4:
            if incode_mandatory:
                raise ValueError('Incode mandatory')
            else:
                return postcode, ''
        # Full postcode
        else:
            return postcode[:-3], postcode[-3:]

if __name__ == '__main__':
    print 'Self test:'
    test_data = [
                 ('cr0 2yr' , False, False, ('CR0' , '2YR')),
                 ('CR0 2YR' , False, False, ('CR0' , '2YR')),
                 ('cr02yr'  , False, False, ('CR0' , '2YR')),
                 ('dn16 9aa', False, False, ('DN16', '9AA')),
                 ('dn169aa' , False, False, ('DN16', '9AA')),
                 ('ec1a 1hq', False, False, ('EC1A', '1HQ')),
                 ('ec1a1hq' , False, False, ('EC1A', '1HQ')),
                 ('m2 5bq'  , False, False, ('M2'  , '5BQ')),
                 ('m25bq'   , False, False, ('M2'  , '5BQ')),
                 ('m34 4ab' , False, False, ('M34' , '4AB')),
                 ('m344ab'  , False, False, ('M34' , '4AB')),
                 ('sw19 2et', False, False, ('SW19', '2ET')),
                 ('sw192et' , False, False, ('SW19', '2ET')),
                 ('w1a 4zz' , False, False, ('W1A' , '4ZZ')),
                 ('w1a4zz'  , False, False, ('W1A' , '4ZZ')),
                 ('cr0'     , False, False, ('CR0' , ''   )),
                 ('sw19'    , False, False, ('SW19', ''   )),
                 ('xx0 2yr' , False, False, ('XX0' , '2YR')),
                 ('3r0 2yr' , False, False, ('3R0' , '2YR')),
                 ('20 2yr'  , False, False, ('20'  , '2YR')),
                 ('3r0 ayr' , False, False, ('3R0' , 'AYR')),
                 ('3r0 22r' , False, False, ('3R0' , '22R')),
                 ('w1m 4zz' , False, False, ('W1M' , '4ZZ')),
                 ('3r0'     , False, False, ('3R0' , ''   )),
                 ('ec1c 1hq', False, False, ('EC1C', '1HQ')),
                 ('m344cb'  , False, False, ('M34' , '4CB')),
                 ('gir 0aa' , False, False, ('GIR' , '0AA')),
                 ('gir'     , False, False, ('GIR' , ''   )),
                 ('w1m 4zz' , False, False, ('W1M' , '4ZZ')),
                 ('w1m'     , False, False, ('W1M' , ''   )),
                 ('dn169aaA', False, False, 'ValueError'   ),
                 
                 ('cr0 2yr' , False, True , ('CR0',  '2YR')),
                 ('CR0 2YR' , False, True , ('CR0' , '2YR')),
                 ('cr02yr'  , False, True , ('CR0',  '2YR')),
                 ('dn16 9aa', False, True , ('DN16', '9AA')),
                 ('dn169aa' , False, True , ('DN16', '9AA')),
                 ('ec1a 1hq', False, True , ('EC1A', '1HQ')),
                 ('ec1a1hq' , False, True , ('EC1A', '1HQ')),
                 ('m2 5bq'  , False, True , ('M2'  , '5BQ')),
                 ('m25bq'   , False, True , ('M2'  , '5BQ')),
                 ('m34 4ab' , False, True , ('M34' , '4AB')),
                 ('m344ab'  , False, True , ('M34' , '4AB')),
                 ('sw19 2et', False, True , ('SW19', '2ET')),
                 ('sw192et' , False, True , ('SW19', '2ET')),
                 ('w1a 4zz' , False, True , ('W1A' , '4ZZ')),
                 ('w1a4zz'  , False, True , ('W1A' , '4ZZ')),
                 ('cr0'     , False, True , 'ValueError'   ),
                 ('sw19'    , False, True , 'ValueError'   ),
                 ('xx0 2yr' , False, True , ('XX0' , '2YR')),
                 ('3r0 2yr' , False, True , ('3R0' , '2YR')),
                 ('20 2yr'  , False, True , ('20'  , '2YR')),
                 ('3r0 ayr' , False, True , ('3R0' , 'AYR')),
                 ('3r0 22r' , False, True , ('3R0' , '22R')),
                 ('w1m 4zz' , False, True , ('W1M' , '4ZZ')),
                 ('3r0'     , False, True , 'ValueError'   ),
                 ('ec1c 1hq', False, True , ('EC1C', '1HQ')),
                 ('m344cb'  , False, True , ('M34' , '4CB')),
                 ('gir 0aa' , False, True , ('GIR' , '0AA')),
                 ('gir'     , False, True , 'ValueError'   ),
                 ('w1m 4zz' , False, True , ('W1M' , '4ZZ')),
                 ('w1m'     , False, True , 'ValueError'   ),
                 ('dn169aaA', False, True , 'ValueError'   ),
                 
                 ('cr0 2yr' , True , False, ('CR0' , '2YR')),
                 ('CR0 2YR' , True , False, ('CR0' , '2YR')),
                 ('cr02yr'  , True , False, ('CR0' , '2YR')),
                 ('dn16 9aa', True , False, ('DN16', '9AA')),
                 ('dn169aa' , True , False, ('DN16', '9AA')),
                 ('ec1a 1hq', True , False, ('EC1A', '1HQ')),
                 ('ec1a1hq' , True , False, ('EC1A', '1HQ')),
                 ('m2 5bq'  , True , False, ('M2'  , '5BQ')),
                 ('m25bq'   , True , False, ('M2'  , '5BQ')),
                 ('m34 4ab' , True , False, ('M34' , '4AB')),
                 ('m344ab'  , True , False, ('M34' , '4AB')),
                 ('sw19 2et', True , False, ('SW19', '2ET')),
                 ('sw192et' , True , False, ('SW19', '2ET')),
                 ('w1a 4zz' , True , False, ('W1A' , '4ZZ')),
                 ('w1a4zz'  , True , False, ('W1A' , '4ZZ')),
                 ('cr0'     , True , False, ('CR0' , ''   )),
                 ('sw19'    , True , False, ('SW19', ''   )),
                 ('xx0 2yr' , True , False, 'ValueError'   ),
                 ('3r0 2yr' , True , False, 'ValueError'   ),
                 ('20 2yr'  , True , False, 'ValueError'   ),
                 ('3r0 ayr' , True , False, 'ValueError'   ),
                 ('3r0 22r' , True , False, 'ValueError'   ),
                 ('w1m 4zz' , True , False, 'ValueError'   ),
                 ('3r0'     , True , False, 'ValueError'   ),
                 ('ec1c 1hq', True , False, 'ValueError'   ),
                 ('m344cb'  , True , False, 'ValueError'   ),
                 ('gir 0aa' , True , False, ('GIR' , '0AA')),
                 ('gir'     , True , False, ('GIR' , ''   )),
                 ('w1m 4zz' , True , False, 'ValueError'   ),
                 ('w1m'     , True , False, 'ValueError'   ),
                 ('dn169aaA', True , False, 'ValueError'   ),
                 
                 ('cr0 2yr' , True , True , ('CR0',  '2YR')),
                 ('CR0 2YR' , True , True , ('CR0' , '2YR')),
                 ('cr02yr'  , True , True , ('CR0',  '2YR')),
                 ('dn16 9aa', True , True , ('DN16', '9AA')),
                 ('dn169aa' , True , True , ('DN16', '9AA')),
                 ('ec1a 1hq', True , True , ('EC1A', '1HQ')),
                 ('ec1a1hq' , True , True , ('EC1A', '1HQ')),
                 ('m2 5bq'  , True , True , ('M2'  , '5BQ')),
                 ('m25bq'   , True , True , ('M2'  , '5BQ')),
                 ('m34 4ab' , True , True , ('M34' , '4AB')),
                 ('m344ab'  , True , True , ('M34' , '4AB')),
                 ('sw19 2et', True , True , ('SW19', '2ET')),
                 ('sw192et' , True , True , ('SW19', '2ET')),
                 ('w1a 4zz' , True , True , ('W1A' , '4ZZ')),
                 ('w1a4zz'  , True , True , ('W1A' , '4ZZ')),
                 ('cr0'     , True , True , 'ValueError'   ),
                 ('sw19'    , True , True , 'ValueError'   ),
                 ('xx0 2yr' , True , True , 'ValueError'   ),
                 ('3r0 2yr' , True , True , 'ValueError'   ),
                 ('20 2yr'  , True , True , 'ValueError'   ),
                 ('3r0 ayr' , True , True , 'ValueError'   ),
                 ('3r0 22r' , True , True , 'ValueError'   ),
                 ('w1m 4zz' , True , True , 'ValueError'   ),
                 ('3r0'     , True , True , 'ValueError'   ),
                 ('ec1c 1hq', True , True , 'ValueError'   ),
                 ('m344cb'  , True , True , 'ValueError'   ),
                 ('gir 0aa' , True , True , ('GIR' , '0AA')),
                 ('gir'     , True , True , 'ValueError'   ),
                 ('w1m 4zz' , True , True , 'ValueError'   ),
                 ('w1m'     , True , True , 'ValueError'   ),
                 ('dn169aaA', True , True , 'ValueError'   ),
                 
                 #('WC2H 8DN', True
                ]
    passes, failures = 0, 0
    for postcode, strict, incode_mandatory, required_result in test_data:
        try:
            actual_result = parse_uk_postcode(postcode, strict, incode_mandatory)
        except ValueError:
            actual_result = 'ValueError'
        if actual_result != required_result:
            failures += 1
            print 'Failed:', repr(actual_result), '!=', repr(required_result), \
                  'for input postcode =', repr(postcode) + \
                  ', strict =', repr(strict) + \
                  ', incode_mandatory =', repr(incode_mandatory)
        else:
            passes += 1
    if failures:
        print failures, "failures. :-("
        print passes, "passed."
    else:
        print passes, "passed! ;-)"

        
def valid_uk_postcode(postcode):
    try:
        parse_uk_postcode(postcode)
        return True
    except ValueError:
        return False

def format_uk_postcode(postcode):
    partA, partB = parse_uk_postcode(postcode.strip())
    return '%s %s' % (partA.upper(), partB.upper())
        

if __name__=='__main__':
    print valid_uk_postcode('WC2H 8DN')