import IntentCard from "./IntentCard";

export default function IntentList({ intents, onSelect }) {
  return (
    // Usa un grid responsivo para mostrar las tarjetas.
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* Mapea cada intent y renderiza la tarjeta */}
      {intents.map((intent) => (
        <IntentCard 
          key={intent} 
          intent={intent} 
          onClick={onSelect} // Cuando se haga clic en la tarjeta, llama a onSelect (definida en App.jsx) con este intent.
        />
      ))}
    </div>
  );
}