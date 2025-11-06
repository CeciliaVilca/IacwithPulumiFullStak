export default function SearchBar({ onSearch }) {
  return (
    <div className="mb-6 flex justify-center">
      <input
        type="text"
        placeholder="Buscar texto o intención..."
        className="w-1/2 p-2 border border-gray-300 rounded-md"
        // Llama a la función padre con el valor actual del input
        onChange={(e) => onSearch(e.target.value)} 
      />
    </div>
  );
}