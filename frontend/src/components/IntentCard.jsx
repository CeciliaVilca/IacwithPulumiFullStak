export default function IntentCard({ intent, onClick }) {
  return (
    <div
      className="p-3 border rounded-md shadow-sm hover:bg-blue-50 cursor-pointer"
      onClick={() => onClick(intent)} // Llama a la función 'onClick' que se pasa desde el padre con el nombre del intent.
    >
      <p className="font-semibold text-gray-700">{intent}</p> {/* Muestra el nombre del intent */}
    </div>
  );
}