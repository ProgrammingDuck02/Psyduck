to do:
-help:
	help ma być po angielsku
	zamiast ? wstaw zmienną prefix
	also, przydałoby się do każdej komendy zrobić szczegółowy opis razem z przykładem albo dwoma
	?party - wyświetla party
	?box <box_number> - wyświetla box o podanym numerze. Domyślnie BOX1
	?switch [poke1] [poke2] - zamienia miejscami dwa pokemony
	?deposit [pokemon] [box/box_number] - wstawia pokemona z teamu do podanego boxa
	?withdraw [box/box_number] [pokemon] - wstawia pokemona z podanego boxa do teamu
	?release pokemon [pokemon_number] in [box/"party"] - wypuszcza pokemona o podanym numerze z podanego miejsca. Specjalnie taka dziwna/długa formułka której by się nie używało gdyby
	?starters - wyświetla dostępne startery
	?pick [number] - wybiera pokemona o podanym numerze jako startera
	?evolution [pokemon name] - pokazuje wszystkie dostępne ewolucje dla danego pokemona oraz jego regionalnych wariantów oraz na którym poziomie ewoluuje
	?evolve [pokemon] <evolution pokemon> - ewoluuje pokemona, jeśli spełnia kryteria do ewolucji. Jeśli podane evolution pokemon, to ewoluuje w pokemona o podanej nazwie (Alolan/Galarian przed nazwą pokemona
		jeśli regionalny wariant). Jeśli evolution pokemon nie podane, a są możliwe 2 lub więcej opcji ewolucji, ewolucja jest losowa. pokemon określa jakiego pokemona chcemy ewoluować. Dla pokemona z party po
		prostu jego numer w party, a dla pokemona z boxa "BOXN:M" gdzie N to numer boxa a M to numer pokemona w tym boxie