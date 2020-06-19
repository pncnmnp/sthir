// Credits_to : https://github.com/pid/murmurHash3js
function get_hashes( word, k , m) {
  hash_indices = []
  for (i = 0; i < k; i++){
    hash_indices.push( murmurHash3.x86.hash32( word, i) % m ) 
  }
  return hash_indices;
}

/*
  list1= ["My" , "name" , "is" , "Mrunank" ];
  text = ""

  for(j=0 ; j< list1.length ; j++){
    text += get_hashes( list1[j], 3 , 20).toString() + "</br>";
  }
  document.getElementById("demo").innerHTML = text
*/
