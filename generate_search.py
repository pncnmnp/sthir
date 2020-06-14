from bitarray import bitarray
import base64

HTML_TEMPLATE = {
    "HEAD":
    """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
        </head>

        <body>
            <pre id="demo"></pre>
            <script>
                function get_bit_array(base64) {
                    let bit_array = [];
                    for (let unicode_char of atob(base64)) {
                        let num = unicode_char.charCodeAt();
                        for (let i = 0; i < 8; i++) {
                            let bit = (num & 0x80) >> 7;
                            bit_array.push(Boolean(bit));
                            num <<= 1;
                        }
                    }
                    return bit_array;
                }
                let demo = document.getElementById("demo");
        """,
    "TAIL":
    """
            let bit_arr = get_bit_array("{}");
            demo.innerHTML = bit_arr.toString();
            </script>
        </body>
        </html>
        """
}
if __name__ == "__main__":
    bit_arr = bitarray()
    with open("document.bin", "rb") as f:
        bit_arr.fromfile(f)
    print(len(bit_arr))
    b64 = base64.b64encode(bit_arr.tobytes())
    with open("output.html","w") as f:
        f.write(HTML_TEMPLATE["HEAD"])
        f.write(HTML_TEMPLATE["TAIL"].format(b64.decode()))
