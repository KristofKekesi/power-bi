[out:csv(::type, ::id, name, tourism, amenity, website)];
area["name"="Magyarország"]->.searchArea;

(
  /* museums */
  node(area.searchArea)[tourism="museum"]->.m;
  way(area.searchArea)[tourism="museum"]->.m;
  relation(area.searchArea)[tourism="museum"]->.m;
  (.m; - .m[amenity~"parking|parking_space"];)

  /* libraries */
  node(area.searchArea)[amenity="library"];
  way(area.searchArea)[amenity="library"];
  relation(area.searchArea)[amenity="library"];
  
  /*node(area.searchArea)[leisure~"stadium|sports_centre|pitch|track"];
  way(area.searchArea)[leisure~"stadium|sports_centre|pitch|track"];
  relation(area.searchArea)[leisure~"stadium|sports_centre|pitch|track"];

  /* castles, forts */
  node(area.searchArea)[historic~"castle|fort"];
  way(area.searchArea)[historic~"castle|fort"];
  relation(area.searchArea)[historic~"castle|fort"];

  way(area.searchArea)[leisure~"park|garden"];
  relation(area.searchArea)[leisure~"park|garden"];

  node(area.searchArea)[tourism~"garden"];
  way(area.searchArea)[tourism~"garden"];
  relation(area.searchArea)[tourism~"garden"];

  /* zoos, aquariums */
  node(area.searchArea)[tourism~"zoo|aquarium"];
  way(area.searchArea)[tourism~"zoo|aquarium"];
  relation(area.searchArea)[tourism~"zoo|aquarium"];

  /* theatres, cinemas */
  node(area.searchArea)[amenity~"theatre|cinema"];
  way(area.searchArea)[amenity~"theatre|cinema"];
  relation(area.searchArea)[amenity~"theatre|cinema"];

  /* galleries, arts centres, exhibition centres */
  node(area.searchArea)[tourism~"gallery"];
  way(area.searchArea)[tourism~"gallery"];
  relation(area.searchArea)[tourism~"gallery"];

  node(area.searchArea)[amenity~"arts_centre|exhibition_centre"];
  way(area.searchArea)[amenity~"arts_centre|exhibition_centre"];
  relation(area.searchArea)[amenity~"arts_centre|exhibition_centre"];

  /* baths, beaches */
  node(area.searchArea)[amenity~"public_bath"];
  way(area.searchArea)[amenity~"public_bath"];
  relation(area.searchArea)[amenity~"public_bath"];
  
);

out center;