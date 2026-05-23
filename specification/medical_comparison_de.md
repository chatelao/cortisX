# Medizinischer Vergleich: Cortisol vs. Cortison

## Übersicht
Cortisol und Cortison sind eng verwandte Corticosteroide, unterscheiden sich jedoch in ihrer biologischen Aktivität und Potenz.

## Biologische Aktivität
- **Cortisol (Hydrocortison)**: Die biologisch aktive Form des Hormons. Es kann direkt an Glucocorticoid-Rezeptoren binden, um seine Wirkung zu entfalten.
- **Cortison**: Ein Prodrug (biologisch inaktiv). Es muss in Cortisol umgewandelt werden, um aktiv zu werden.

## Aktivierungsweg
Die Umwandlung von Cortison in Cortisol wird durch das Enzym **11β-Hydroxysteroid-Dehydrogenase Typ 1 (11β-HSD1)** vermittelt, das sich hauptsächlich in der Leber befindet, aber auch in anderen Geweben wie dem Fettgewebe und dem Gehirn vorkommt. Umgekehrt wird Cortisol durch **11β-HSD2**, vor allem in den Nieren, wieder in Cortison umgewandelt.

![Chemisches Gleichgewicht: Cortison <=> Cortisol](output/images/chemical_balance.png)

### Der Mechanismus des 11β-HSD1-Enzyms

Die Umwandlung von Cortison in Cortisol ist ein entscheidender Schritt bei der Aktivierung von Glucocorticoiden. Diese Reaktion wird durch die **11β-Hydroxysteroid-Dehydrogenase Typ 1 (11β-HSD1)** katalysiert.

#### Enzymstruktur und aktives Zentrum
11β-HSD1 ist ein membrangebundenes Enzym, das zur Familie der Short-Chain-Dehydrogenasen/-Reduktasen (SDR) gehört. Es fungiert in vivo primär als Reduktase und nutzt **NADPH** als Cofaktor.

Das aktive Zentrum besteht aus mehreren Schlüsselkomponenten:
- **Katalytische Triade**: Die Reste **Ser170**, **Tyr183** und **Lys187** sind essentiell für den Hydridtransfer vom NADPH auf das Steroidsubstrat.
- **Cofaktor (NADPH)**: Bindet in einer spezifischen Orientierung, um die notwendigen Reduktionsäquivalente bereitzustellen.
- **Substratbindetasche**: Speziell geformt, um den Steroidkern von Cortisol und Cortison aufzunehmen, wobei sichergestellt wird, dass die C11-Position perfekt auf die katalytischen Reste ausgerichtet ist.

![Nahaufnahme des aktiven Zentrums von 11β-HSD1 (PDB 1XU7)](output/images/enzyme_11bhsd1_active_site.png)

![11β-HSD1 Enzym (PDB 1XU7) mit hervorgehobenem aktivem Zentrum (NDP und katalytische Reste)](output/images/enzyme_11bhsd1.png)

## Pharmakologische Bedeutung und klinische Relevanz
Die klinische Relevanz dieser Moleküle wird durch ihre biologische Aktivität und therapeutische Wirksamkeit definiert.
- **Cortisol (Hydrocortison)**: Als aktives Hormon stellt es den primären Vermittler von Glucocorticoid-Effekten dar. Seine pharmakologische Bedeutung liegt in seiner sofortigen Verfügbarkeit für die Rezeptorbindung, was es für die akute Ersatztherapie und Notsituationen (z. B. Addison-Krise) unerlässlich macht.
- **Cortison**: Seine Qualität als Medikament ist durch seine Rolle als Prodrug gekennzeichnet. Es erfordert eine metabolische Aktivierung, was zu einem langsameren Wirkungseintritt im Vergleich zur direkten Cortisol-Verabreichung führt. Dies macht es geeignet für chronische Erkrankungen, bei denen eine gleichmäßigere, weniger akute Wirkung erwünscht ist.

## Relative Potenz
- **Cortisol**: Relative Potenz = 1 (Referenzstandard).
- **Cortison**: Relative Potenz ≈ 0,8. Cortison gilt im Allgemeinen als etwas weniger potent als Cortisol, da eine enzymatische Aktivierung erforderlich ist.

## Signalkette
Der Signalweg von Cortisol (und aktiviertem Cortison) umfasst mehrere unterschiedliche Stadien:
1. **Zelleintritt**: Da Cortisol lipophil ist, diffundiert es frei durch die Zellmembran in das Zytoplasma.
2. **Rezeptorbindung**: Im Zytoplasma bindet Cortisol an den **[Glucocorticoid-Rezeptor (NR3C1 / GR)](https://www.proteinatlas.org/ENSG00000113580-NR3C1)**, der normalerweise durch einen Chaperon-Komplex, bestehend aus **[HSP90 (HSP90AA1)](https://www.proteinatlas.org/ENSG00000080824-HSP90AA1)**, **[HSP70 (HSPA1A)](https://www.proteinatlas.org/ENSG00000204389-HSPA1A)** und **[FKBP5](https://www.proteinatlas.org/ENSG00000096060-FKBP5)** (das die Bindungsaffinität reduziert), in einem inaktiven Zustand gehalten wird.
3. **Aktivierung**: Die Bindung löst die Dissoziation dieser Chaperon-Proteine aus. Dabei wird FKBP5 oft durch **[FKBP4](https://www.proteinatlas.org/ENSG00000004478-FKBP4)** ersetzt, was die Konformationsänderung unterstützt und die Bindungsaffinität erhöht.
4. **Nukleare Translokation**: Der aktivierte Cortisol-GR-Komplex transloziert in den Zellkern, wobei FKBP4 die Interaktion mit dem **[Dynein-Transportprotein (DYNC1H1)](https://www.proteinatlas.org/ENSG00000197102-DYNC1H1)** vermittelt.
5. **Biologische Reaktion**:
    - **Transaktivierung**: Der Komplex bindet an spezifische DNA-Sequenzen, die als **Glucocorticoid-Response-Elements (GREs)** bezeichnet werden, und stimuliert die Transkription von entzündungshemmenden und metabolischen Genen.
    - **Transrepression**: Der Komplex kann auch die Aktivität anderer Transkriptionsfaktoren wie **[NF-κB (NFKB1)](https://www.proteinatlas.org/ENSG00000109320-NFKB1)** oder **[AP-1 (JUN)](https://www.proteinatlas.org/ENSG00000177606-JUN)** stören und dadurch die Expression proinflammatorischer Gene unterdrücken.

## Therapeutische Anwendungsfälle
### Cortisol (Hydrocortison)
- **Nebenniereninsuffizienz**: Primäre Behandlung der Addison-Krankheit.
- **Akute allergische Reaktionen**: Wird für eine schnelle Wirkung bei schweren Allergien eingesetzt.
- **Topische Anwendungen**: Häufig in Cremes gegen Hautentzündungen und Juckreiz.

### Cortison
- **Gelenk- und Sehnenentzündungen**: Historisch als „Cortisonspritze“ bekannt, wobei heute meist synthetische Derivate wie Triamcinolon oder direkt wirksames Hydrocortison verwendet werden, da Cortison vor Ort erst aktiviert werden müsste.
- **Systemische Entzündungen**: Wird oral bei verschiedenen Autoimmun- und Entzündungskrankheiten eingesetzt, bei denen ein Prodrug-Ansatz akzeptabel ist.

## Hauptunterschiede
| Merkmal | Cortisol (Hydrocortison) | Cortison |
|---------|---------------------------|-----------|
| **Form** | Aktives Hormon | Inaktives Prodrug |
| **Primärer Wirkort** | Systemisch / Gewebe | Muss in Leber/Gewebe aktiviert werden |
| **Halbwertszeit** | Plasma: ~1,5 - 2 h; Biologisch: 8 - 12 h | Plasma: ~0,5 - 1 h (schnelle Aktivierung) |
| **Mineralocorticoid-Aktivität** | Hoch (potenziell), aber enzymatisch geschützt | Keine (inaktiv am Rezeptor) |
