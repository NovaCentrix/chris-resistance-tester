#!/usr/bin/env python3

import time
import binascii

# Micropython doesn't have .zfill(w) function
# this replacement from their forums:
def zfill(s, width):
  # Pads the provided string with leading 0's to suit the specified 'chrs' length
  # Force # characters, fill with leading 0's
  return '{:0>{w}}'.format(s, w=width)

class Bool_confirmed:
  UNK = 0
  TRUE = 1
  FALSE = 2
  ERROR = 3
  BSTRING = [ 'x', 'T', 'F', 'e' ]
  MIN = 0
  MAX = 3
  def from_bool(self, value):
    if value: self.flag = self.TRUE
    else:     self.flag = self.FALSE
  def from_string(self, value):
    if len(value)==0:
      self.flag = self.UNK
    #else:
    #  if value[0].lower in (b.lower() for b in self.BSTRING):
    #    self.flag=self.BSTRING.index(value[0])
    #  else:
    #    self.flag = self.UNK
    else:
      if value[0].lower() in (b.lower() for b in self.BSTRING):
        self.flag = next( i for i,v in enumerate(self.BSTRING) \
                              if v.lower() == value[0].lower() )
      else:
        self.flag = self.ERROR
  def to_string(self):
    return __str__(self)
  def __init__(self, flag=None):
    if flag is None: self.flag = self.UNK
    elif flag > self.MAX: self.flag = self.ERROR
    elif flag < self.MIN: self.flag = self.ERROR
    else: self.flag = flag
  def __bool__(self):
    return self.flag == self.TRUE
  def __eq__(a,b):
    if a.valid() and b.valid():
      return a.flag == b.flag
    else:
      return False
  def valid(self):
    return self.flag == self.TRUE or self.flag == self.FALSE
  def __str__(self):
    return self.BSTRING[ self.flag ]
  def __repr__(self):
    return self.__str__()

class Packet_type:
  # packet type will always contain valid string
  # flag self.unknown will be set, however, if an
  # invalid string was used to initialize the 
  # packet type
  PTYPE_DEF = 'pksend'
  PTYPES = { 'pksend': 'PKSEND', 
             'pkecho': 'PKECHO', 
             'acknak': 'ACKNAK',
          }
  def __init__(self, stype=None):
    self.set_ptype(stype)
  def __eq__(a,b):
    return a.ptype == b.ptype
  def __str__(self):
    return '{}'.format(self.ptype)
  def __repr__(self):
    return self.__str__()
  def validate(self, stype):
    return stype.lower() in self.PTYPES
  def set_ptype(self, stype=None):
    if stype is None: stype = self.PTYPE_DEF
    if self.validate(stype):
      self.unknown = False
      self.ptype = self.PTYPES[stype.lower()]
    else:
      self.unknown = True
      self.ptype = self.PTYPES[self.PTYPE_DEF]

class Hex_value:
  # size is nibbles, not bytes
  @classmethod
  def check_hex(cls,text):
    # hexdigits = string.hexdigits: 
    # Micropython doesn't have string module
    hexdigits = '0123456789abcdefABCDEF'
    for ch in text:
      if ch not in hexdigits: 
        return False
    return True
  def __init__(self, value=0, size=4, vmin=None, vmax=None):
    self.ival = None
    self.size = size
    if vmin is None:
      self.vmin = 0
    else:
      self.vmin = vmin
    if vmax is None:
      self.vmax = pow(2,self.size*4)
    else:
      self.vmax = vmax
    if isinstance(value, str):
      self.from_string(value)
    elif isinstance(value, int):
      self.from_int(value)
    if self.ival is None:
      self.default()
  def default(self):
    self.ival = 0
    self.hval = zfill('0', self.size)
  def limits(self, value):
    if self.vmin is not None \
       and self.vmax is not None:
      return value >= self.vmin and value < self.vmax
    return True
  def from_int(self, value):
    self.default()
    if self.limits(value):
      self.ival = value
      self.hval = zfill( hex(value)[2:], self.size )
    return self
  def from_string(self, text):
    if self.check_hex(text) and len(text)<=self.size:
      self.ival = int(text,16)
      self.hval = zfill(text, self.size)
      if not self.limits(self.ival):
        self.default()
      return self
  def __eq__(a,b):
    return a.ival == b.ival
  def __gt__(a,b):
    return a.ival > b.ival
  def __str__(self):
    return '{:5d}\t0x{}'.format(self.ival, self.hval)
  def __repr__(self):
    return __str__()
  def __int__(self):
    return self.ival

class Parsing_status:
  def __init__(self):
    self.init_bools()
    self.set_lengths()
  def init_bools(self):
    # initialized all to unknown
    self.sync = Bool_confirmed()
    self.chret = Bool_confirmed()
    self.fields = Bool_confirmed()
    self.size_packet = Bool_confirmed()
    self.size_size = Bool_confirmed()
    self.size_crc = Bool_confirmed()
    self.size_payload = Bool_confirmed()
    self.hex_size = Bool_confirmed()
    self.hex_crc = Bool_confirmed()
    self.crc = Bool_confirmed()
    self.valid = Bool_confirmed()
  def set_lengths( self, lpacket=0, lsync=0, lsize=0, lpayload=0, lcrc=0 ):
    self.len_packet = lpacket
    self.len_sync = lsync
    self.len_size = lsize
    self.len_payload = lpayload
    self.len_crc = lcrc
  def __bool__(self):
    return all( [
      self.sync, 
      self.chret, 
      self.fields, 
      self.size_packet, 
      self.size_size, 
      self.size_crc, 
      self.size_payload, 
      self.hex_size, 
      self.hex_crc, 
      self.crc, 
      ] )
  def __str__(self):
    return \
      '\nlen of packet.....>  {}  bytes'.format( self.len_packet ) +\
      '\nlen of sync.......>  {}  bytes'.format( self.len_sync ) +\
      '\nlen of size.......>  {}  bytes'.format( self.len_size ) +\
      '\nlen of payload....>  {}  bytes'.format( self.len_payload ) +\
      '\nlen of crc........>  {}  bytes'.format( self.len_crc ) +\
      '\nsync..............>  {}  sync pattern must be PACKET'.format( self.sync ) +\
      '\nchret.............>  {}  packet must end with CR'.format( self.chret ) +\
      '\nfields............>  {}  must be three unit separators'.format( self.fields ) +\
      '\nsize of packet....>  {}  must be 22 bytes or larger'.format( self.size_packet ) +\
      '\nsize of size......>  {}  must be four bytes'.format( self.size_size ) +\
      '\nsize of crc.......>  {}  must be eight bytes'.format( self.size_crc ) +\
      '\nsize of payload...>  {}  must agree with size in packet'.format( self.size_payload ) +\
      '\nsize valid hex....>  {}  contains valid hexadecimal characters'.format( self.hex_size ) +\
      '\ncrc valid hex.....>  {}  contains valid hexadecimal characters'.format( self.hex_crc ) +\
      '\ncrc is valid......>  {}  crc calculations match crc in packet'.format( self.crc )
  def __repr__(self):
    return self.__str__()
  def serialize(self):
    return \
      '{},{},{},{},{};'.format( \
          self.len_packet, self.len_sync, self.len_size,\
          self.len_payload, self.len_crc ) + \
      '{},{},{},{},{},{},{},{},{},{}'.format( 
          self.sync, self.chret, self.fields,
          self.size_packet, self.size_size, self.size_crc,
          self.size_payload, self.hex_size, self.hex_crc,
          self.crc )
  def unserialize(self, text):
    parts = text.strip().split(';')
    if len(parts) != 2: 
      self.init_bools()
      self.set_lengths()
      return False
    nums = parts[0].split(',')
    if len(nums) != 5:
      self.init_bools()
      self.set_lengths()
      return False
    flags = parts[1].split(',')
    if len(flags) != 10: 
      self.init_bools()
      self.set_lengths()
      return False
    self.len_packet   = nums[0]
    self.len_sync     = nums[1]
    self.len_size     = nums[2]
    self.len_payload  = nums[3]
    self.len_crc      = nums[4]
    self.sync.from_string(         flags[0] )
    self.chret.from_string(        flags[1] )
    self.fields.from_string(       flags[2] )
    self.size_packet.from_string(  flags[3] )
    self.size_size.from_string(    flags[4] )
    self.size_crc.from_string(     flags[5] )
    self.size_payload.from_string( flags[6] )
    self.hex_size.from_string(     flags[7] )
    self.hex_crc.from_string(      flags[8] )
    self.crc.from_string(          flags[9] )
    return True

class Packet:
  # Packet:
  # PACKET\t(LEN)\t(payload-goes-here)\t(crc)\n
  #   6   sync always 6 bytes
  #   4   len always 4 hex bytes
  #   x   payload variables length
  #   8   crc always 8 bytes
  #   4   US characters 3 + cr 1 
  #  22 + x  Total Packet Size
  OVERHEAD = 22
  USEP = '\x1f'
  RSEP = '\x1e'
  def __init__(self, payload='', stype=None):
    self.vb=False # verbosity
    self.generate(payload, stype)
  def __eq__(a,b):
    return a.sync == b.sync and \
           a.payload == b.payload and \
           a.size == b.size and \
           a.crc == b.crc
  def __str__(self):
    #return '{}\t{}\t{}\t{} ({})'.format(
    return '{} / {} / {} / {}'.format(
        self.sync, self.size.hval, self.payload, self.crc.hval )
  def __repr__(self):
    return self.__str__()
  def raw(self):
    return self.packet
  
  def build(self):
    self.packet = self.USEP.join([str(self.sync), self.size.hval, self.payload, self.crc.hval]) + '\r'

  def reset(self):
    self.generate()

  def generate(self, payload='', stype=None):
    self.sync = Packet_type(stype)
    self.payload = payload
    self.size = Hex_value(len(self.payload), size=4)
    crc = binascii.crc32(bytes(self.payload,'latin_1'))
    self.crc = Hex_value( crc, size=8)
    self.build()

  def parse(self, packet):
    status = Parsing_status()
    pktsize = len(packet)
    status.len_packet = pktsize
    status.size_packet.from_bool( pktsize >= self.OVERHEAD )
    if self.vb: print('packet size:', pktsize)
    if status.size_packet:
      status.chret.from_bool( packet.endswith('\r') )
      if self.vb: print('ends with CR:', status.chret)
      fields = packet.strip().split(self.USEP)
      num_fields = len(fields)
      status.fields.from_bool( num_fields == 4 )
      if self.vb: print('number of fields:', num_fields)
      if status.fields:
        if self.vb: print('fields0.sync:', fields[0])
        if self.vb: print('fields1.size:', fields[1])
        if self.vb: print('fields2.payl:', fields[2])
        if self.vb: print('fields3.crc :', fields[3])
        status.len_sync = len(fields[0])
        status.len_size = len(fields[1])
        status.len_payload = len(fields[2])
        status.len_crc = len(fields[3])
        status.size_size.from_bool( len(fields[1]) == 4 )
        status.size_crc.from_bool( len(fields[3]) == 8 )
        status.hex_size.from_bool( Hex_value.check_hex(fields[1]) )
        status.hex_crc.from_bool( Hex_value.check_hex(fields[3]) )
        sync = Packet_type( fields[0] )
        status.sync.from_bool( not sync.unknown )
        size = Hex_value(fields[1], size=4)
        payload = fields[2]
        crc = Hex_value(fields[3], size=8)
        if self.vb: print('sync:', sync)
        if self.vb: print('size:', size)
        if self.vb: print('payl:', payload)
        if self.vb: print(' crc:', crc)
        if self.vb: print('stat.size_size:', status.size_size)
        if self.vb: print('stat.size_crc:', status.size_crc)
        if self.vb: print('stat.hex_size:', status.hex_size)
        if self.vb: print('stat.hex_crc:', status.hex_crc)
        if all([ 
            status.chret, status.sync, 
            status.size_size, status.size_crc,
            status.hex_size, status.hex_crc 
        ] ):
          if self.vb: print('all okay')
          status.size_payload.from_bool( len(payload) == size.ival )
          if self.vb: print('stat.size_payload:', status.size_payload )
          if status.size_payload:
            crc_calc = Hex_value( binascii.crc32(bytes(payload,'latin_1')), size=8 )
            if self.vb: print('crc_calc:', crc_calc)
            status.crc.from_bool( crc == crc_calc )
            if self.vb: print('stat.crc:', status.crc )
            if status.crc:
              if self.vb: print('finally!!!!')
              if self.vb: print('sync:', sync)
              if self.vb: print('size:', size)
              if self.vb: print('payload:', payload)
              if self.vb: print('crc:', crc)
              self.sync = sync
              self.size = size
              self.payload = payload
              self.crc = crc
              self.build()
    if not status:
      self.reset()

    return status

  @classmethod
  def serialize(cls, text):
    return text.replace(cls.USEP,'{US}').replace('\r','{CR}')

  @classmethod
  def unserialize(cls, text):
    return text.replace( '{US}', cls.USEP ).replace('{CR}', '\r' )


def testme(message='hello'):
  #message = 'hello'
  #if True:

  print('====Generated packet p:')
  p = Packet()
  p.generate(message)
  print('message:', message)
  print('P Packet:')
  print(p)


  print('====Parsed packet p2:')
  toparse = p.raw()
  p2 = Packet()
  p2_status = p2.parse(toparse)
  print('toparse:', toparse)
  print('P2 Packet:')
  print(p2)

  print('====Reply un-tabbed payload packet pr:')
  pr = Packet()
  serial_msg = pr.serialize(toparse)
  pr.generate(serial_msg)
  print('serialized:', serial_msg)
  print('PR Packet:')
  print(pr)

  print('====Extract from received packet pck:')
  reply = pr.raw()
  pck = Packet()
  pck_status = pck.parse(reply)
  print('reply:', reply)
  print('Packet:')
  print(pck)

  print('====Extracted packet again from payload:')
  kmsg = pck.payload
  print('Extracted payload:', kmsg)
  p0 = Packet()
  unserial_msg = p0.unserialize(kmsg)
  print('Unserialized payload:', unserial_msg)
  p0_status = p0.parse(unserial_msg)
  print('P0 Original Packet:')
  print(p0)




#if __name__ == "__main__":
#  main()

class Code_point:
  def __init__(self, code, uni, abbr, descr):
    self.code = code
    self.uni = uni
    self.abbr = abbr 
    self.descr = descr

class Ascii:
  def __init__(self):
    print('size, bytes', len(self.ASCII_DESCRIPTION))
    self.table = self.ASCII_DESCRIPTION.splitlines() 
    print('size, lines', len(self.table))
    self.codes = []
    for line in self.table:
      #print(line)
      code, uni, abbr, descr = line.split('\t')
      #print(code, uni, abbr, descr)
      self.codes.append( Code_point(code, uni, abbr, descr) )




  ASCII_DESCRIPTION=\
  """0x00	'u+0000	NUL	null character'
     0x01	'u+0001	SOH	start of heading'
     0x02	'u+0002	STX	start of text'
     0x03	'u+0003	ETX	end of text'
     0x04	'u+0004	EOT	end of transmission'
     0x05	'u+0005	ENQ	enquiry'
     0x06	'u+0006	ACK	acknowledge'
     0x07	'u+0007	BEL	bell'
     0x08	'u+0008	BS	backspace'
     0x09	'u+0009	HT	horizontal tab'
     0x0a	'u+000a	LF	new line'
     0x0b	'u+000b	VT	vertical tab'
     0x0c	'u+000c	FF	form feed'
     0x0d	'u+000d	CR	carriage ret'
     0x0e	'u+000e	SO	shift out'
     0x0f	'u+000f	SI	shift in'
     0x10	'u+0010	DLE	data link escape'
     0x11	'u+0011	DC1	device control 1'
     0x12	'u+0012	DC2	device control 2'
     0x13	'u+0013	DC3	device control 3'
     0x14	'u+0014	DC4	device control 4'
     0x15	'u+0015	NAK	negative ack.'
     0x16	'u+0016	SYN	synchronous idle'
     0x17	'u+0017	ETB	end of trans. blk'
     0x18	'u+0018	CAN	cancel'
     0x19	'u+0019	EM 	end of medium'
     0x1a	'u+001a	SUB	substitute'
     0x1b	'u+001b	ESC	escape'
     0x1c	'u+001c	FS	file separator'
     0x1d	'u+001d	GS	group separator'
     0x1e	'u+001e	RS	record separator'
     0x1f	'u+001f	US	unit separator'
     0x20	'u+0020	 	space'
     0x21	'u+0021	!	exclamation mark'
     0x22	'u+0022	"	quotation mark'
     0x23	'u+0023	#	number sign'
     0x24	'u+0024	$	dollar sign'
     0x25	'u+0025	%	percent sign'
     0x26	'u+0026	&	ampersand'
     0x27	'u+0027	\	 apostrophe'
     0x28	'u+0028	(	left parenthesis'
     0x29	'u+0029	)	right parenthesis'
     0x2a	'u+002a	*	asterisk'
     0x2b	'u+002b	+	plus sign'
     0x2c	'u+002c	,	comma'
     0x2d	'u+002d	-	hyphen-minus'
     0x2e	'u+002e	.	full stop'
     0x2f	'u+002f	/	solidus'
     0x30	'u+0030	0	digit zero'
     0x31	'u+0031	1	digit one'
     0x32	'u+0032	2	digit two'
     0x33	'u+0033	3	digit three'
     0x34	'u+0034	4	digit four'
     0x35	'u+0035	5	digit five'
     0x36	'u+0036	6	digit six'
     0x37	'u+0037	7	digit seven'
     0x38	'u+0038	8	digit eight'
     0x39	'u+0039	9	digit nine'
     0x3a	'u+003a	:	colon'
     0x3b	'u+003b	;	semicolon'
     0x3c	'u+003c	<	less-than sign'
     0x3d	'u+003d	=	equals sign'
     0x3e	'u+003e	>	greater-than sign'
     0x3f	'u+003f	?	question mark'
     0x40	'u+0040	@	commercial at'
     0x41	'u+0041	A	latin capital letter A'
     0x42	'u+0042	B	latin capital letter B'
     0x43	'u+0043	C	latin capital letter C'
     0x44	'u+0044	D	latin capital letter D'
     0x45	'u+0045	E	latin capital letter E'
     0x46	'u+0046	F	latin capital letter F'
     0x47	'u+0047	G	latin capital letter G'
     0x48	'u+0048	H	latin capital letter H'
     0x49	'u+0049	I	latin capital letter I'
     0x4a	'u+004a	J	latin capital letter J'
     0x4b	'u+004b	K	latin capital letter K'
     0x4c	'u+004c	L	latin capital letter L'
     0x4d	'u+004d	M	latin capital letter M'
     0x4e	'u+004e	N	latin capital letter N'
     0x4f	'u+004f	O	latin capital letter O'
     0x50	'u+0050	P	latin capital letter P'
     0x51	'u+0051	Q	latin capital letter Q'
     0x52	'u+0052	R	latin capital letter R'
     0x53	'u+0053	S	latin capital letter S'
     0x54	'u+0054	T	latin capital letter T'
     0x55	'u+0055	U	latin capital letter U'
     0x56	'u+0056	V	latin capital letter V'
     0x57	'u+0057	W	latin capital letter W'
     0x58	'u+0058	X	latin capital letter X'
     0x59	'u+0059	Y	latin capital letter Y'
     0x5a	'u+005a	Z	latin capital letter Z'
     0x5b	'u+005b	[	left square bracket'
     0x5c	'u+005c	\\	 reverse solidus'
     0x5d	'u+005d	]	right square bracket'
     0x5e	'u+005e	^	circumflex accent'
     0x5f	'u+005f	_	low line'
     0x60	'u+0060	`	grave accent'
     0x61	'u+0061	a	latin small letter a'
     0x62	'u+0062	b	latin small letter b'
     0x63	'u+0063	c	latin small letter c'
     0x64	'u+0064	d	latin small letter d'
     0x65	'u+0065	e	latin small letter e'
     0x66	'u+0066	f	latin small letter f'
     0x67	'u+0067	g	latin small letter g'
     0x68	'u+0068	h	latin small letter h'
     0x69	'u+0069	i	latin small letter i'
     0x6a	'u+006a	j	latin small letter j'
     0x6b	'u+006b	k	latin small letter k'
     0x6c	'u+006c	l	latin small letter l'
     0x6d	'u+006d	m	latin small letter m'
     0x6e	'u+006e	n	latin small letter n'
     0x6f	'u+006f	o	latin small letter o'
     0x70	'u+0070	p	latin small letter p'
     0x71	'u+0071	q	latin small letter q'
     0x72	'u+0072	r	latin small letter r'
     0x73	'u+0073	s	latin small letter s'
     0x74	'u+0074	t	latin small letter t'
     0x75	'u+0075	u	latin small letter u'
     0x76	'u+0076	v	latin small letter v'
     0x77	'u+0077	w	latin small letter w'
     0x78	'u+0078	x	latin small letter x'
     0x79	'u+0079	y	latin small letter y'
     0x7a	'u+007a	z	latin small letter z'
     0x7b	'u+007b	{	left curly bracket'
     0x7c	'u+007c	|	vertical line'
     0x7d	'u+007d	}	right curly bracket'
     0x7e	'u+007e	~	tilde'
     0x7f	'u+007f	DEL	tilde'"""

