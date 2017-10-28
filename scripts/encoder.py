from io import StringIO


class Encoder:
    BASE66_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~"
    BASE = len(BASE66_ALPHABET)

    def __init__(self,
                 alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~"):
        self.alphabet = alphabet
        self.base = len(alphabet)

    def encode(self, msg):

        msg = self.alphabet[self.base - 1] + msg

        i = 0

        for c in msg:
            i = i * self.base + self.alphabet.index(c)

        if i == 0:
            return Encoder.BASE66_ALPHABET[0]

        r = StringIO()
        while i:
            i, t = divmod(i, Encoder.BASE)
            r.write(Encoder.BASE66_ALPHABET[t])
        return r.getvalue()[::-1]

    def decode(self, alpha) -> str:
        i = 0

        for c in alpha:
            i = i * Encoder.BASE + Encoder.BASE66_ALPHABET.index(c)

        if i == 0:
            return Encoder.BASE66_ALPHABET[0]

        r = StringIO()
        while i:
            i, t = divmod(i, self.base)
            r.write(self.alphabet[t])
        return r.getvalue()[::-1][1:]

    def encode_games_array(self, arr):
        games_str = str(arr)
        games_str = games_str.lstrip('[')
        games_str = games_str.rstrip(']')
        games_str = games_str.replace(', ', 'a')
        return self.encode(games_str)

    def decode_user_games_alpha(self, alpha):
        string = self.decode(alpha)
        arr = string.split("a")
        int_arr = [int(x) for x in arr]
        return int_arr
