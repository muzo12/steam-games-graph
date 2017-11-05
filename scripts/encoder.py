from io import StringIO


class Encoder:
    base66_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.~"
    base11_alphabet = "0123456789a"

    def __init__(self):
        pass

    @staticmethod
    def translate(phrase,
                  source_alphabet,
                  target_alphabet) -> str:

        i = 0
        source_base = len(source_alphabet)
        target_base = len(target_alphabet)

        for c in phrase:
            i *= source_base
            i += source_alphabet.find(c)

        r = StringIO()
        while i:
            i, t = divmod(i, target_base)
            r.write(target_alphabet[t])
        return r.getvalue()[::-1]

    def encode_games_array(self, arr):
        games_str = str(arr)
        games_str = games_str.lstrip('[')
        games_str = games_str.rstrip(']')
        games_str = games_str.replace(', ', 'a')
        games_str = self.base11_alphabet[len(self.base11_alphabet) - 1] + games_str

        alpha = self.translate(phrase=games_str,
                               source_alphabet=self.base11_alphabet,
                               target_alphabet=self.base66_alphabet)
        return alpha

    def decode_games_string(self, alpha):
        string = self.translate(phrase=alpha,
                                source_alphabet=self.base66_alphabet,
                                target_alphabet=self.base11_alphabet)[1:]
        arr = string.split("a")
        int_arr = [int(x) for x in arr]
        return int_arr
