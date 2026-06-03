"""
SAT-authentic Reading & Writing passages.

Format conventions (rendered by frontend):
  [[blank]]       → underlined blank  _______ (vocabulary / grammar fill-in)
  **text**        → underlined/highlighted text (craft & structure questions)
  [CHART: ...]    → rendered as a styled data table / figure box
  [TABLE: ...]    → same, tabular layout

Each passage is 25–150 words, academic/literary/historical/scientific.
Domain tags: "craft_structure" | "info_ideas" | "standard_english" | "expression_ideas"
"""

# Each entry: (passage_text, domain_hint)
PASSAGES = [
    # ── Information & Ideas ────────────────────────────────────────────────
    (
        "A 2023 study published in *Nature Climate Change* examined the relationship between urban tree canopy coverage and local surface temperatures. Researchers analyzed satellite data from 97 cities across six continents. They found that every 10% increase in canopy coverage corresponded to a 0.9°C reduction in daytime surface temperature. The effect was largest in cities located in arid climates, where shade is most scarce. The authors concluded that strategic urban reforestation could be a cost-effective tool for reducing heat-island effects without requiring significant infrastructure investment.",
        "info_ideas"
    ),
    (
        "Sociologist Arlie Hochschild introduced the concept of the **\"second shift\"** in her 1989 book of the same name. She argued that employed women, after completing their paid workday, routinely returned home to perform the majority of domestic labor — cooking, cleaning, and childcare. This unpaid work constituted a second full job. Hochschild's data showed that, on average, women worked an extra month of 24-hour days per year compared to their male partners. Subsequent decades of research have confirmed that this gap, while narrowing, persists across industrialized nations.",
        "info_ideas"
    ),
    (
        "The Columbian Exchange, initiated by Christopher Columbus's 1492 voyage, fundamentally reshaped global agriculture. Crops indigenous to the Americas — including potatoes, maize, tomatoes, and cacao — were introduced to Europe, Africa, and Asia, transforming diets and enabling population growth in regions where these calorie-dense foods thrived. Conversely, Old World crops such as wheat, sugar cane, and coffee were transplanted to the Americas. Historians estimate that New World crops now account for roughly one-third of global food production, making the exchange one of the most consequential ecological events in human history.",
        "info_ideas"
    ),
    (
        "Bioluminescence — the production and emission of light by living organisms — has evolved independently at least 94 times across the tree of life. Marine organisms account for the vast majority of bioluminescent species, including anglerfish, dinoflagellates, and certain species of jellyfish and squid. Scientists hypothesize that bioluminescence serves multiple functions depending on the organism: attracting prey, deterring predators, communicating with potential mates, or camouflaging against downwelling sunlight. Despite decades of study, researchers have identified bioluminescence in fewer than 1% of terrestrial species, suggesting the deep ocean remains the primary ecological niche for this adaptation.",
        "info_ideas"
    ),
    (
        "In her landmark 1962 work *Silent Spring*, marine biologist Rachel Carson documented the environmental damage caused by widespread pesticide use, particularly DDT. Carson argued that pesticides did not stay where they were applied — they moved through food chains, concentrating in the fatty tissues of predators and causing reproductive failures in bird populations. Her book triggered a national debate that culminated in the 1972 ban on DDT in the United States and the creation of the Environmental Protection Agency. Critics initially dismissed her as alarmist, but subsequent ecological research has largely validated her findings.",
        "info_ideas"
    ),
    (
        "Astronomers have long debated whether the universe's expansion is accelerating. In 1998, two independent research teams studying Type Ia supernovae discovered that distant supernovae appeared dimmer than expected — suggesting they were farther away than standard cosmological models predicted. This finding implied that the universe was not only expanding but **accelerating** in its expansion, driven by a mysterious force they termed **dark energy**. The discovery earned the 2011 Nobel Prize in Physics. Today, dark energy is estimated to constitute approximately 68% of the total energy content of the observable universe, yet its fundamental nature remains unknown.",
        "info_ideas"
    ),
    (
        "[CHART: Estimated global plastic waste generation (million metric tons)\nYear | Total Waste | Ocean-Bound Waste\n2000 | 213         | 8.1\n2005 | 260         | 9.8\n2010 | 302         | 11.5\n2015 | 381         | 13.2\n2019 | 460         | 14.9]\n\nThe data above were compiled by the Our World in Data research group using national waste management reports. Ocean-bound waste refers to plastic generated within 50 kilometers of a coastline in countries with inadequate waste management infrastructure.",
        "info_ideas"
    ),
    (
        "[CHART: Percentage of adults reporting regular exercise (≥150 min/week)\nIncome Quintile | 2010 | 2015 | 2020\nLowest          | 28%  | 31%  | 33%\nSecond          | 34%  | 37%  | 39%\nMiddle          | 41%  | 44%  | 46%\nFourth          | 49%  | 52%  | 55%\nHighest         | 58%  | 62%  | 65%]\n\nThe figures above are drawn from the National Health Interview Survey. Researchers noted that access to safe recreational spaces, gym memberships, and discretionary time all correlate with income level, which may help explain the observed pattern.",
        "info_ideas"
    ),
    (
        "Researchers studying collective behavior in starlings observed that flocks of thousands of birds — called murmurations — move with a coherence that appears to defy individual processing speeds. Using high-speed cameras and computer modeling, the scientists found that each starling responds only to its **seven nearest neighbors**, regardless of flock density. This local interaction rule, replicated across the entire group, produces the sweeping, coordinated movements visible from the ground. The study has since influenced research in robotics, where engineers seek to replicate such emergent coordination in swarms of autonomous drones.",
        "info_ideas"
    ),
    (
        "During World War II, the United States government relocated approximately 120,000 people of Japanese ancestry — roughly two-thirds of whom were American citizens — into internment camps following Executive Order 9066. Conditions in the camps were austere: families lived in barracks, endured extreme temperatures, and faced restrictions on movement. Economic losses for internees were estimated at $1.3 billion in 1942 dollars. In 1988, the Civil Liberties Act formally acknowledged the injustice and provided reparations of $20,000 to surviving internees. The episode is widely cited in legal scholarship as a cautionary example of wartime civil liberties violations.",
        "info_ideas"
    ),

    # ── Craft & Structure ──────────────────────────────────────────────────
    (
        "The following is adapted from a 2021 essay by environmental journalist Elizabeth Kolbert.\n\nWhen the last woolly mammoth died — probably on Wrangel Island, in the Arctic Ocean, about four thousand years ago — it had no idea it was the last. Neither, presumably, did it know it was a woolly mammoth. As far as we know, only humans are aware of extinction as a concept, and only humans have caused it on a significant scale. **This is the peculiar burden of consciousness: we can recognize catastrophes that we ourselves have set in motion.**",
        "craft_structure"
    ),
    (
        "The following text is from a 2020 policy brief on urban housing.\n\nCities have long struggled to balance competing demands for land. In San Francisco, a decade of restrictive zoning ordinances intended to preserve neighborhood character has produced an unintended consequence: a severe shortage of housing that has pushed median rents above $3,000 per month. Advocates for deregulation argue that **allowing taller, denser buildings near transit corridors** would increase supply and moderate prices. Opponents counter that such development inevitably displaces lower-income residents before new units are affordable. The debate reflects a broader tension between growth and preservation that no simple policy can fully resolve.",
        "craft_structure"
    ),
    (
        "Adapted from a 2019 profile of marine ecologist Sylvia Earle.\n\nEarle has described the ocean as **\"the blue heart of the planet\"** — a phrase that captures both its centrality to Earth's life-support systems and the emotional resonance she feels toward it. Now in her late eighties, she has logged more than seven thousand hours underwater, led more than a hundred expeditions, and founded the nonprofit Mission Blue, which works to establish protected marine reserves worldwide. Critics sometimes dismiss her advocacy as romanticized. But her scientific credentials are unimpeachable: she has described more than thirty species new to science and led the first team of women aquanauts to live and work on the ocean floor.",
        "craft_structure"
    ),
    (
        "The following is from a 2022 literary review.\n\nIn her debut novel, Yaa Gyasi employs a multi-generational structure that spans three centuries and two continents. Each chapter follows a different descendant of two Ghanaian half-sisters, one of whom was sold into slavery and the other of whom married a British colonizer. The novel's form itself becomes an argument: by refusing to privilege any single character's perspective, Gyasi insists that the consequences of the transatlantic slave trade cannot be confined to a single life or a single era. **The architecture of the book is its thesis.**",
        "craft_structure"
    ),
    (
        "Sociologist Erving Goffman introduced the concept of **\"face-work\"** to describe the strategies people use to maintain their own and others' social standing in everyday interactions. According to Goffman, individuals are constantly managing impressions — adjusting their speech, posture, and behavior to conform to the social roles they inhabit. Far from being superficial, this performative dimension of social life is, in Goffman's view, what makes cooperative society possible. Without the tacit agreements that govern face-to-face interaction, social order would be perpetually at risk of disruption.",
        "craft_structure"
    ),

    # ── Standard English Conventions (grammar/punctuation) ────────────────
    (
        "Urban planners in Copenhagen have spent decades designing infrastructure around the bicycle rather than the automobile. Today, more than 60 percent of residents cycle to work or school daily, a figure [[blank]] surpassed by no other major city in the world. The city maintains over 400 kilometers of dedicated cycling lanes, many of which are physically separated from both pedestrian and vehicle traffic. Officials credit this infrastructure investment with reducing congestion, lowering carbon emissions, and improving public health outcomes across income levels.",
        "standard_english"
    ),
    (
        "In 1869, Russian chemist Dmitri Mendeleev organized the known elements into a table arranged by atomic weight. What distinguished his version from earlier attempts was his willingness to leave gaps: where the pattern demanded an element that had not yet been discovered, Mendeleev [[blank]] a space and predicted its properties. Three of those predictions — for gallium, scandium, and germanium — were confirmed within fifteen years, validating the periodic table's underlying logic and cementing its place as the organizing framework of modern chemistry.",
        "standard_english"
    ),
    (
        "The migratory monarch butterfly undertakes one of the most remarkable journeys in the animal kingdom. Each fall, populations east of the Rocky Mountains travel up to 4,800 kilometers from Canada and the northern United States to overwintering sites in the forests of central Mexico. What makes this feat particularly astonishing [[blank]] the fact that no individual butterfly has ever made the journey before: each migration is completed by a generation that has never seen the destination. Scientists believe monarchs navigate using a time-compensated sun compass located in their antennae.",
        "standard_english"
    ),
    (
        "Psychologist Carol Dweck's research on motivation distinguishes between two mindsets. Students with a **fixed mindset** believe their abilities are innate and unchangeable; they tend to avoid challenges that risk exposing their limitations. Students with a **growth mindset**, [[blank]], believe that abilities can be developed through effort and practice; they tend to embrace challenges as opportunities for improvement. Dweck's experimental interventions, which teach students the neuroscience of learning, have produced measurable gains in academic performance in controlled studies across multiple countries.",
        "standard_english"
    ),
    (
        "When architects Renzo Piano and Richard Rogers unveiled the Centre Pompidou in Paris in 1977, critics were divided. The building turned its functional systems — elevators, escalators, ventilation ducts, and water pipes — [[blank]] to the outside, color-coded by purpose: blue for air, green for water, yellow for electrical systems, and red for circulation. Some observers celebrated it as a bold rejection of architectural convention; others derided it as an industrial eyesore in a historic city. Today, it ranks among the most visited cultural institutions in the world.",
        "standard_english"
    ),
    (
        "The following sentence contains a blank. Choose the word or phrase that best completes the sentence while maintaining grammatical correctness and logical meaning.\n\nMarine biologist Sylvia Earle, [[blank]] has logged more than seven thousand hours underwater, argues that fewer than five percent of the ocean has been meaningfully explored — a statistic she uses to underscore the urgency of deep-sea conservation efforts.",
        "standard_english"
    ),

    # ── Expression of Ideas (revision / rhetorical synthesis) ─────────────
    (
        "A student is writing a research paper arguing that social media platforms should be required to label algorithmically amplified content. The student has found the following sources:\n\n**Source 1:** A 2021 MIT study found that false news spreads six times faster on social media than true news, partly because false stories tend to be more novel and emotionally provocative.\n\n**Source 2:** A 2022 Pew Research survey found that 64% of American adults believe social media has a mostly negative effect on the way things are going in the country.\n\n**Source 3:** Facebook's internal research, leaked in 2021, showed that its algorithm amplified outrage-inducing content because it generated more engagement.",
        "expression_ideas"
    ),
    (
        "A student is writing a paper about the health effects of ultra-processed foods. She wants to add a sentence explaining why correlation studies have limitations. She has found the following information:\n\n**Fact A:** People who eat more ultra-processed foods tend to have higher rates of obesity and cardiovascular disease.\n\n**Fact B:** People who eat more ultra-processed foods also tend to have lower incomes, less access to healthcare, and higher stress levels.\n\n**Fact C:** A 2022 randomized controlled trial found that participants assigned to an ultra-processed diet consumed 500 more calories per day than those assigned a whole-foods diet, even when both groups had equal access to food.",
        "expression_ideas"
    ),
    (
        "The following paragraph is from a student's essay about the Apollo 11 mission. The student wants to add a sentence that **most effectively transitions** from the description of the mission's technical challenges to its cultural impact.\n\n\"The Apollo 11 mission required solving engineering problems that had no precedent in human history. The Saturn V rocket, at 111 meters tall, was the most powerful machine ever built. Guidance computers with less processing power than a modern digital watch had to navigate astronauts to the lunar surface and back. _______ On the evening of July 20, 1969, an estimated 600 million people — one-fifth of the world's population — watched Neil Armstrong step onto the Moon.\"",
        "expression_ideas"
    ),
    (
        "A researcher studying sleep deprivation wants to revise the following sentence to make it more precise:\n\n**Original:** \"Not getting enough sleep is bad for people and affects how they think and feel.\"\n\nThe researcher has found the following data:\n- Adults who sleep fewer than 6 hours per night show a 48% increased risk of cardiovascular disease.\n- Sleep deprivation impairs prefrontal cortex function, reducing working memory capacity and emotional regulation.\n- The CDC classifies insufficient sleep (fewer than 7 hours per night) as a public health epidemic.\n\nWhich revision most effectively improves the precision and credibility of the original sentence?",
        "expression_ideas"
    ),
    (
        "While researching a paper on renewable energy, a student encounters the following two claims:\n\n**Claim 1 (from a solar industry report):** \"Solar energy capacity in the United States grew by 43% in 2023 alone, demonstrating that renewable energy is rapidly becoming the dominant source of electricity.\"\n\n**Claim 2 (from the U.S. Energy Information Administration):** \"Renewable energy sources, including solar and wind, accounted for approximately 21% of total U.S. electricity generation in 2023, up from 17% in 2020.\"\n\nThe student wants to use the most accurate and balanced statement of solar energy's current role. Which of the following best reconciles the two sources?",
        "expression_ideas"
    ),

    # ── Additional Information & Ideas (charts + data) ────────────────────
    (
        "[CHART: Average global surface temperature anomaly (°C relative to 1951–1980 average)\nDecade    | Anomaly\n1880–1889 | −0.17\n1910–1919 | −0.26\n1940–1949 | +0.02\n1970–1979 | +0.01\n2000–2009 | +0.57\n2010–2019 | +0.82\n2020–2022 | +0.98]\n\nThe data above are from NASA's Goddard Institute for Space Studies. Scientists use a baseline average from 1951 to 1980 as the reference point because global temperature records from that period are particularly complete and reliable.",
        "info_ideas"
    ),
    (
        "[TABLE: Results of a 2021 study on study technique effectiveness (n = 1,200 college students)\nTechnique          | Avg. Test Score | Improvement over control\nRe-reading         | 68%             | +2%\nHighlighting       | 69%             | +3%\nSummarizing        | 74%             | +8%\nPractice testing   | 83%             | +17%\nSpaced repetition  | 85%             | +19%]\n\nResearchers noted that despite practice testing and spaced repetition producing the largest gains, surveys showed that only 11% of students reported using these techniques regularly, while 72% reported re-reading as their primary study method.",
        "info_ideas"
    ),
    (
        "Primatologist Jane Goodall's 1960 observation that chimpanzees at Gombe Stream used stripped grass stems as tools to extract termites from mounds forced a revision of the scientific definition of *Homo sapiens*. Until that point, the capacity to make and use tools was considered a defining characteristic of humans alone. When Goodall cabled the finding to her mentor, Louis Leakey, he famously replied: **\"Now we must redefine tool, redefine Man, or accept chimpanzees as humans.\"** Subsequent fieldwork has documented tool use in dozens of animal species, fundamentally changing how scientists conceptualize human uniqueness.",
        "info_ideas"
    ),
    (
        "The placebo effect — the measurable improvement in a patient's condition following a treatment with no active pharmacological ingredient — has been documented across hundreds of clinical trials. What has surprised researchers is that the effect persists even in **open-label** studies, in which patients are explicitly told they are receiving a placebo. A 2010 trial led by Ted Kaptchuk found that irritable bowel syndrome patients who knowingly took placebos reported significantly greater symptom improvement than those who received no treatment. These findings suggest that the ritual of treatment itself — the clinical encounter, the taking of a pill — triggers genuine physiological responses.",
        "info_ideas"
    ),
    (
        "Linguist Noam Chomsky proposed the concept of **universal grammar** — the hypothesis that all human languages share a set of underlying structural rules encoded in the human brain. His key evidence was that children acquire their native language with remarkable speed and accuracy despite receiving what he called **\"poverty of the stimulus\"**: they master grammatical rules from relatively limited and imperfect input. Critics have challenged universal grammar on cross-linguistic grounds, arguing that the world's roughly 7,000 languages show far more structural diversity than Chomsky's model predicts. The debate remains one of the most contested in cognitive science.",
        "info_ideas"
    ),
    (
        "In 2012, Fei-Fei Li and her colleagues released ImageNet, a database of over fourteen million labeled photographs, along with a competition challenging teams to build algorithms that could classify images accurately. The winning entry that year — a deep convolutional neural network called AlexNet — achieved an error rate of 15.3%, nearly half that of the second-place entry. AlexNet's performance shocked the computer vision community and triggered a wave of investment in deep learning. Within five years, image-recognition algorithms achieved human-level accuracy on benchmark tasks, marking a turning point in the development of artificial intelligence.",
        "info_ideas"
    ),
    (
        "Epidemiologist John Snow's 1854 investigation of a cholera outbreak in London's Soho neighborhood is considered a founding moment of modern epidemiology. At a time when cholera was widely believed to be spread through contaminated air (**\"miasma\"**), Snow mapped the locations of cases and deaths and found that they clustered around a single water pump on Broad Street. His data convinced local authorities to remove the pump handle, ending the outbreak. Snow's work established the methodological principle that understanding disease requires mapping its distribution in populations — a principle that remains central to public health practice today.",
        "info_ideas"
    ),
    (
        "The following passage is adapted from a 2023 profile in *The Atlantic*.\n\nFor decades, CRISPR-Cas9 was primarily a curiosity of bacterial immune systems. Then, in 2012, biochemist Jennifer Doudna and microbiologist Emmanuelle Charpentier published a paper showing that the system could be reprogrammed to cut DNA at precise locations — essentially a molecular find-and-replace tool. The implications were immediate and staggering. Within months, laboratories around the world were using CRISPR to edit plant genomes, disable viral sequences, and, eventually, correct the mutations responsible for genetic diseases. The 2020 Nobel Prize in Chemistry, awarded to Doudna and Charpentier, recognized not merely a discovery but **a new chapter in the story of life itself**.",
        "info_ideas"
    ),
    (
        "[CHART: Public trust in selected institutions (% reporting \"a great deal\" or \"quite a lot\" of trust)\nInstitution        | 2000 | 2010 | 2023\nMilitary           | 64%  | 76%  | 60%\nSmall business     | 58%  | 66%  | 65%\nSupreme Court      | 47%  | 49%  | 27%\nPublic schools     | 37%  | 34%  | 26%\nNewspapers         | 37%  | 25%  | 18%\nCongress           | 24%  | 11%  | 8%]\n\nSource: Gallup polling, 2000–2023. Researchers note that declining institutional trust correlates with increased political polarization, though the direction of causality remains debated.",
        "info_ideas"
    ),
    (
        "The \"grandfather paradox\" is the most famous challenge to the theoretical possibility of time travel. If a person traveled back in time and prevented their grandfather from meeting their grandmother, the time traveler would never have been born — and therefore could never have traveled back in time to prevent the meeting. Physicist David Deutsch proposed a resolution using the **many-worlds interpretation** of quantum mechanics: in his model, the time traveler arrives in a parallel branch of reality, not in their own past, thus avoiding the contradiction entirely. Most physicists, however, regard backward time travel as physically impossible regardless of such theoretical workarounds.",
        "info_ideas"
    ),
    (
        "Art historian Linda Nochlin's 1971 essay **\"Why Have There Been No Great Women Artists?\"** challenged the assumption embedded in its own title. Rather than arguing that women lacked genius, Nochlin demonstrated that institutional structures — the exclusion of women from life-drawing classes, the prohibition on professional training, the expectation of domesticity — had systematically prevented women from acquiring the conditions necessary to produce canonical art. Her argument shifted the terms of feminist art history from a search for overlooked female geniuses to an analysis of the social conditions that produced and policed artistic greatness.",
        "craft_structure"
    ),
    (
        "In ecology, the term **\"keystone species\"** refers to an organism whose presence has a disproportionately large effect on its ecosystem relative to its abundance. The concept was introduced by zoologist Robert Paine in 1969, following his observation that removing sea stars from a tidal pool triggered a collapse of biodiversity: mussels, freed from predation, crowded out dozens of other species. The keystone metaphor captures the essential idea — just as a single stone at the crown of an arch holds the structure together, a keystone species maintains the structural integrity of an ecosystem. Its removal, even from a position of apparent low prominence, can cause the entire arch to fall.",
        "craft_structure"
    ),
    (
        "Cognitive psychologists distinguish between **\"fast\" and \"slow\" thinking** — terms popularized by Daniel Kahneman in his 2011 book *Thinking, Fast and Slow*. Fast thinking is automatic, intuitive, and effortless; it allows us to navigate familiar situations without expending conscious effort. Slow thinking is deliberate, analytical, and effortful; it is required for complex calculations, logical reasoning, and decisions with significant consequences. Kahneman's research shows that humans are systematically prone to errors when fast thinking is applied to situations that require slow thinking — a tendency he calls **cognitive bias**. Recognizing this tendency, he argues, is the first step toward better decision-making.",
        "craft_structure"
    ),
    (
        "The following is adapted from a 2022 essay on conservation biology.\n\nFor most of human history, extinction was understood as a natural, if tragic, feature of life on Earth. Species came and went; the fossil record attested to waves of mass extinction long before *Homo sapiens* arrived. What is unprecedented about the current moment is not extinction itself but its rate. Scientists estimate that species are now disappearing at 100 to 1,000 times the background rate — the rate that would occur in the absence of human activity. Some researchers have begun calling this accelerating loss the **\"sixth mass extinction\"**, placing it in the company of the five great die-offs that reshaped the history of life.",
        "craft_structure"
    ),
    (
        "Mathematician Emmy Noether, described by Albert Einstein as \"the most significant creative mathematical genius thus far produced,\" made fundamental contributions to abstract algebra and theoretical physics. Her 1915 theorem — now known simply as **Noether's theorem** — demonstrated that every symmetry in the laws of physics corresponds to a conserved quantity. The conservation of energy, for example, follows from the fact that the laws of physics are the same today as they were yesterday. Despite the theorem's central importance to modern physics, Noether was denied a paid academic position for years because she was a woman, eventually holding an unofficial faculty role at the University of Göttingen.",
        "info_ideas"
    ),
    (
        "To investigate whether plants respond to acoustic stimuli, researchers at the University of Missouri exposed corn seedlings to recordings of caterpillar feeding sounds — the vibrations produced as an insect chews through a leaf. Control plants were kept in silence. After 24 hours, the plants exposed to feeding sounds produced significantly higher concentrations of defensive chemicals — **glucosinolates and anthocyanins** — than the control group. The researchers concluded that plants may use vibrational signals as an early-warning system, mounting chemical defenses before a predator makes physical contact. The finding challenges the traditional view of plants as passive organisms.",
        "info_ideas"
    ),
    (
        "Behavioral economists Amos Tversky and Daniel Kahneman identified a systematic bias they called **\"loss aversion\"**: the tendency for people to prefer avoiding losses over acquiring equivalent gains. In a classic experiment, participants were given $50 and offered a choice: keep $30 with certainty, or flip a coin to either keep all $50 or lose it all. Despite the identical expected values, most participants chose the certain option. Tversky and Kahneman estimated that losses are psychologically approximately twice as powerful as gains of the same magnitude. Loss aversion helps explain a range of apparently irrational economic behaviors, from investor reluctance to sell declining stocks to consumer preference for \"no-loss\" framing in advertising.",
        "info_ideas"
    ),
    (
        "[TABLE: Voter turnout in U.S. presidential elections by age group\nAge Group | 2008 | 2012 | 2016 | 2020\n18–29     | 51%  | 45%  | 43%  | 52%\n30–44     | 62%  | 59%  | 58%  | 65%\n45–59     | 69%  | 67%  | 66%  | 71%\n60+       | 73%  | 72%  | 71%  | 76%]\n\nSource: U.S. Census Bureau, Current Population Survey. Researchers note that the 2020 election saw increases in turnout across all age groups, with the largest percentage-point gain among voters aged 18–29 compared to 2016.",
        "info_ideas"
    ),
    (
        "Architect Zaha Hadid became the first woman to receive the Pritzker Architecture Prize — often described as the Nobel Prize of architecture — in 2004. Her designs were characterized by fragmented geometry, dynamic curved forms, and a rejection of right angles that she described as reflecting \"the chaos and flow of contemporary life.\" The Heydar Aliyev Center in Baku, Azerbaijan, completed in 2012, is perhaps her most celebrated work: a building in which walls, floor, and ceiling flow into each other without visible joints, creating the impression of a single continuous surface. Critics have described it as a building that **\"dissolves the boundary between architecture and landscape.\"**",
        "craft_structure"
    ),
    (
        "Ecologist E.O. Wilson argued throughout his career that humanity is in the grip of what he called **\"biophilia\"** — an innate emotional affiliation with other living organisms. Unlike most evolutionary hypotheses about human preferences, Wilson's claim was that this affinity was not merely learned but was encoded in our biology through millions of years of coevolution with the natural world. Evidence for biophilia is largely indirect: studies showing that hospital patients with window views of nature recover faster, that urban residents with access to green spaces report lower stress levels, and that children consistently prefer natural environments over built ones in experimental settings.",
        "info_ideas"
    ),
    (
        "The following passage is from a 2020 report on antibiotic resistance.\n\nWhen Alexander Fleming discovered penicillin in 1928, he warned — even in his Nobel acceptance speech — that misuse of the drug could produce resistant bacteria. His prophecy has proven accurate. Today, the World Health Organization estimates that antimicrobial resistance kills approximately 1.27 million people annually and is projected to cause 10 million deaths per year by 2050. The primary drivers are overprescription in human medicine and routine preventive use in livestock farming. Unlike most medical threats, antibiotic resistance is a **\"tragedy of the commons\"**: every individual use of an antibiotic degrades a shared resource that belongs to the entire species.",
        "info_ideas"
    ),
    (
        "The Turing Test, proposed by mathematician Alan Turing in 1950, offers an operational definition of machine intelligence: a computer passes the test if a human interrogator, communicating via text, cannot reliably distinguish its responses from those of a human. Turing framed the test as a substitute for the unanswerable question \"Can machines think?\" Critics have argued that passing the Turing Test proves only that a machine can **simulate** intelligence, not that it possesses genuine understanding. Philosopher John Searle's **\"Chinese Room\"** thought experiment makes this point: a person following rules to manipulate Chinese symbols could pass for a Chinese speaker without understanding a word of Chinese.",
        "craft_structure"
    ),
    (
        "The concept of **\"social capital\"** — the networks of relationships, norms of reciprocity, and trust that enable people to cooperate effectively — was developed by sociologist Pierre Bourdieu in the 1980s and later popularized by political scientist Robert Putnam. Putnam's 2000 book *Bowling Alone* documented a decline in civic participation in the United States, arguing that Americans were becoming increasingly isolated from the community institutions — bowling leagues, parent-teacher associations, religious congregations — that had previously built social capital. Whether digital social networks compensate for this decline or accelerate it remains a contested empirical question.",
        "info_ideas"
    ),
    (
        "Virologist Peter Doherty and immunologist Rolf Zinkernagel shared the 1996 Nobel Prize in Physiology or Medicine for discovering how the immune system recognizes virus-infected cells. Their key insight was that T cells do not recognize pathogens in isolation; rather, they recognize **viral fragments displayed on the surface of host cells** in combination with proteins encoded by the major histocompatibility complex (MHC). This dual-recognition mechanism explained why immune cells are specific to both a particular virus and a particular host's tissue type — a finding with profound implications for organ transplantation, vaccine design, and autoimmune disease research.",
        "info_ideas"
    ),
    (
        "[CHART: Global renewable energy capacity additions (gigawatts) by technology\nYear | Solar PV | Wind | Hydropower | Other\n2015 | 56       | 63   | 28         | 12\n2017 | 99       | 52   | 19         | 10\n2019 | 118      | 60   | 15         | 11\n2021 | 168      | 93   | 26         | 12\n2023 | 345      | 117  | 23         | 14]\n\nSource: International Renewable Energy Agency (IRENA), Renewable Power Generation Costs, 2024. Analysts attribute solar PV's accelerating growth primarily to dramatic reductions in manufacturing costs: the price of solar panels fell approximately 90% between 2010 and 2023.",
        "info_ideas"
    ),
    (
        "The concept of the **\"invisible hand\"** — the idea that individual self-interest, operating through competitive markets, tends to promote social welfare without deliberate coordination — was introduced by Adam Smith in *The Wealth of Nations* (1776). Smith's metaphor has been enormously influential, but scholars note that he used it sparingly and that its modern application often overstates his argument. Smith himself recognized that markets could fail in cases of monopoly, information asymmetry, and public goods — circumstances in which the invisible hand does not reliably convert private interest into public benefit. The selective reading of Smith has become a recurring topic in the history of economic thought.",
        "info_ideas"
    ),
    (
        "Historian Eric Hobsbawm coined the term **\"invented traditions\"** to describe practices that appear ancient but are in fact recent creations designed to establish continuity with a suitable historical past. The Scottish Highland tradition — kilts, clan tartans, and bagpipes — is among his most cited examples: though presented as timeless Celtic custom, most of its contemporary forms were codified or invented in the eighteenth and nineteenth centuries, often by Lowland Scots and English enthusiasts rather than Highland communities. Hobsbawm argued that invented traditions are particularly prevalent during periods of rapid social change, when societies seek to anchor new institutions in the legitimizing weight of apparent antiquity.",
        "info_ideas"
    ),
    (
        "Developmental biologist Conrad Waddington proposed the metaphor of the **\"epigenetic landscape\"** in 1957 to describe how a cell's developmental fate becomes increasingly constrained as it matures. In Waddington's image, a ball rolls down a hillside divided by ridges into valleys; as it descends, it is progressively channeled into one valley or another, each representing a distinct cell type. The metaphor anticipated modern findings about cell differentiation — the process by which a single fertilized egg gives rise to hundreds of specialized cell types — and continues to inform research on stem cells, cancer, and the possibility of cellular reprogramming.",
        "info_ideas"
    ),
    (
        "Philosopher of science Thomas Kuhn argued in *The Structure of Scientific Revolutions* (1962) that science does not progress through the steady accumulation of knowledge but through **\"paradigm shifts\"** — episodes in which an entire framework of assumptions is overturned and replaced. Normal science, in Kuhn's account, consists of puzzle-solving within an accepted paradigm; anomalies accumulate until the framework can no longer accommodate them, triggering a crisis that resolves only when a new paradigm emerges. The Copernican revolution, which displaced Earth from the center of the cosmos, and the Darwinian revolution, which replaced the concept of fixed species, are his central examples.",
        "info_ideas"
    ),
    (
        "In 2003, the Human Genome Project announced the completion of a reference sequence for the human genome — the approximately 3.2 billion base pairs of DNA contained in human cells. The project took thirteen years and cost approximately $2.7 billion. By 2022, the cost of sequencing an individual human genome had fallen to approximately $200, and turnaround time had dropped from years to hours. This dramatic cost reduction has enabled population-scale genomic studies that were inconceivable at the project's outset, transforming fields from personalized medicine to evolutionary biology. [CHART: Cost of genome sequencing per genome\n2001: $100,000,000\n2007: $10,000,000\n2012: $10,000\n2017: $1,000\n2022: $200]",
        "info_ideas"
    ),
    (
        "Anthropologist Margaret Mead's 1928 study *Coming of Age in Samoa* argued that the emotional turmoil associated with adolescence in Western societies was culturally determined, not biologically inevitable. Samoan teenagers, she claimed, transitioned to adulthood with relative ease because their culture imposed fewer repressive sexual norms. Her findings were celebrated as evidence for cultural relativism and used to challenge biological determinism. In 1983, however, anthropologist Derek Freeman published a detailed critique arguing that Mead had been misled by her informants and that Samoan adolescence was in fact marked by considerable stress and conflict. The controversy has never been fully resolved.",
        "info_ideas"
    ),
    (
        "The **\"overview effect\"** is a term coined by writer Frank White to describe the cognitive and emotional shift reported by astronauts who view Earth from space. Astronauts consistently describe an overwhelming sense of the planet's fragility, a dissolution of national and political boundaries, and a heightened appreciation for the interconnectedness of all life. Edgar Mitchell, who walked on the Moon during Apollo 14, described a sudden conviction that the universe was **\"in some way conscious\"** — an experience he spent decades attempting to integrate into a scientific framework. Psychologists have begun studying the effect to understand whether analogous experiences can be induced on Earth through immersive technologies.",
        "info_ideas"
    ),
    (
        "The following passage is adapted from a 2021 article on behavioral economics.\n\nTraditional economic models assume that consumers make rational decisions when choosing between options, carefully weighing costs and benefits. But behavioral economists have repeatedly demonstrated that **framing** — the way a choice is presented — dramatically influences decisions even when the underlying options are identical. In a classic study, participants rated ground beef labeled **\"75% lean\"** significantly more favorably than beef labeled **\"25% fat\"**, despite the descriptions being mathematically equivalent. Such findings have transformed public policy: governments now routinely use \"nudges\" — default options, simplified disclosures, and strategic framing — to steer citizens toward choices that improve their health, finances, and environmental impact.",
        "info_ideas"
    ),
    (
        "Geologist Marie Tharp spent years in the 1950s mapping the ocean floor from depth-sounding data collected by research vessels. Her meticulous cartographic work revealed a continuous mountain range running through the center of every ocean basin — the **Mid-Ocean Ridge** — and, crucially, a rift valley running along its crest. This rift, Tharp argued, was evidence of seafloor spreading: new oceanic crust was being created at the ridges and moving outward, driving the motion of the continents. Her male colleagues initially dismissed the interpretation as **\"girl talk.\"** Within a decade, the evidence for plate tectonics was overwhelming, and Tharp's maps had become foundational documents of modern geology.",
        "info_ideas"
    ),
    (
        "[TABLE: Effects of exercise on cognitive performance (meta-analysis of 55 studies)\nExercise type     | Effect on memory | Effect on attention | Effect on processing speed\nAerobic (acute)   | +12%             | +15%                | +9%\nAerobic (chronic) | +17%             | +20%                | +14%\nStrength training | +8%              | +11%                | +6%\nYoga/mind-body    | +10%             | +13%                | +7%]\n\nResearchers noted significant heterogeneity across studies due to differences in participant age, exercise intensity, and cognitive assessment methods. The largest effects were observed in older adults and individuals with cognitive impairment at baseline.",
        "info_ideas"
    ),
    (
        "Philosopher Hannah Arendt introduced the concept of the **\"banality of evil\"** following her coverage of the trial of Adolf Eichmann, a Nazi official who organized the logistics of the Holocaust. Arendt was struck by Eichmann's ordinariness: he was not a fanatic or a monster but a bureaucrat who described his role in mass murder in the banal language of administrative procedure. His evil, she argued, was not demonic but **thoughtless** — a failure to think from the perspective of others, a surrender of moral judgment to institutional authority. The phrase has been applied to atrocities ever since, though some scholars have challenged its applicability to the Holocaust specifically.",
        "craft_structure"
    ),
    (
        "In the 1960s, economists Gary Becker and George Stigler developed the concept of **\"rational addiction\"**: the idea that even addictive behaviors can be modeled as rational choices, with individuals effectively trading future well-being for present pleasure. Their model predicted that addicts are not simply victims of compulsion but are making informed, if suboptimal, intertemporal trade-offs. Critics argued the model failed to account for the neurological evidence that addiction hijacks the brain's reward circuitry in ways that undermine genuine choice. The debate between economic and neurological frameworks for understanding addiction remains active, with significant implications for public policy on drug treatment and criminal justice.",
        "info_ideas"
    ),
    (
        "The first photograph of a black hole — specifically the supermassive black hole at the center of the galaxy M87 — was released by the Event Horizon Telescope collaboration in April 2019. The image, which shows a bright ring of light surrounding a dark central region, was produced by combining data from eight radio observatories located on four continents, effectively creating a telescope the size of Earth. The ring's appearance matched the predictions of general relativity with striking precision. Team leader Sheperd Doeleman described it as **\"direct visual evidence of a supermassive black hole in the center of a galaxy.\"** The data processing required to produce the image took two years and generated over five petabytes of raw data.",
        "info_ideas"
    ),
]
