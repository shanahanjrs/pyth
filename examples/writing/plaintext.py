from pyth3.plugins.plaintext.writer import PlaintextWriter
import pythonDoc

doc = pythonDoc.buildDoc()

print PlaintextWriter.write(doc).getvalue()
