import re
import intervaltree

class Rescue:

    class Status:
        descriptions = {
            '?': 'copying non-tried blocks',
            '*': 'trimming non-trimmed blocks',
            '/': 'scraping non-scraped blocks',
            '-': 'retrying bad sectors',
            'F': 'filling the blocks specified',
            'G': 'generating approximate mapfile',
            '+': 'finished',
        }

        def __init__(self, input_position, current_pass, status):
            self.input_position = input_position
            self.current_pass = current_pass
            self.status = status

        def is_finished(self):
            return self.status == '+'

        def __str__(self):
            return 'ddrescue is {} at {}, pass {}'.format(
                Rescue.Status.descriptions[self.status],
                self.input_position,
                self.current_pass
            )

        def __repr__(self):
            return '<Rescue.Status {} @{} #{}>'.format(
                self.status,
                self.input_position,
                self.current_pass
            )

    class Block:
        descriptions = {
            '?': 'non-tried block',
            '*': 'failed block non-trimmed',
            '/': 'failed block non-scraped',
            '-': 'failed block bad-sector(s)',
            '+': 'finished block',
        }

        def __init__(self, start, end, size, status):
            self.start = start
            self.end = end
            self.size = size
            self.status = status

        def __str__(self):
            return '{} at {} to {} exclusive, {} bytes'.format(
                Rescue.Block.descriptions[self.status],
                self.start,
                self.end,
                self.size
            )

        def __repr__(self):
            return '<Rescue.Block {} @[{}, {}) = {}>'.format(
                self.status,
                self.start,
                self.end,
                self.size
            )

    def __init__(self):
        self.status = None
        self.bad_blocks = intervaltree.IntervalTree()

    def is_finished(self):
        return self.status.is_finished() and not self.bad_blocks

class Map:
    line_comment = re.compile(r'^\s*#.*$')
    line_status = re.compile(r'^\s*0[xX][0-9a-fA-F]+\s+[?*\/\-FG+]\s+[1-9]+\s*$')
    line_block = re.compile(r'^\s*0[xX][0-9a-fA-F]+\s+0[xX][0-9a-fA-F]+\s+[?*\/\-+]\s*$')
    hexadecimal = re.compile(r'0[xX][0-9a-fA-F]+')
    positive_decimal = re.compile(r'[1-9]+')
    rescue_status = re.compile(r'[?*\/\-FG+]')
    block_status = re.compile(r'[?*\/\-+]')

    class ParseError(Exception):
        pass

    def parse(io):
        rescue = Rescue()

        for line in io:
            line = line.strip()

            if Map.line_comment.match(line):
                continue

            if rescue.status is None:
                if Map.line_status.match(line):
                    input_position, status, current_pass = line.split()

                    input_position = int(input_position, 16)
                    current_pass   = int(current_pass,   10)

                    rescue.status = Rescue.Status(
                        input_position,
                        current_pass,
                        status
                    )

                else:
                    raise Map.ParseError('Expected status line')
            else:
                if Map.line_block.match(line):
                    start, size, status = line.split()

                    if status == '+':
                        continue

                    start = int(start, 16)
                    size = int(size, 16)
                    end = start + size

                    block = Rescue.Block(start, end, size, status)
                    rescue.bad_blocks[start:end] = block

                else:
                    raise Map.ParseError('Expected data block line')

        return rescue
