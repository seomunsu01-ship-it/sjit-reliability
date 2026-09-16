from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('<script id="reliabilityFinalGuard">')
end=s.find('</script>',start)
if start>=0 and end>start:
    block=s[start:end+9]
    # The previous generator used a raw Python string and accidentally wrote literal
    # backslash-n sequences. Convert only inside this guard back to real newlines.
    block=block.replace('\\n','\n')
    s=s[:start]+block+s[end+9:]
    p.write_text(s,encoding='utf-8')
    print('guard normalized')
else:
    print('guard not found')
