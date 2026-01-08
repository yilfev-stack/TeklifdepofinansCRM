const ProposalCover = ({ proposal }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    if (proposal.language === 'english') {
      return date.toLocaleDateString('en-US', { day: '2-digit', month: 'long', year: 'numeric' });
    }
    return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  return (
    <div 
      className="relative w-full h-full overflow-hidden bg-white"
      data-testid="proposal-cover"
    >
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-[0.30]"
        style={{
          backgroundImage: "url('/images/background.jpg')"
        }}
      />
      
      {/* Content */}
      <div className="relative h-full px-12 py-10 flex flex-col z-20">
        {/* Top Section - Logo and Teklif No with Representative */}
        <div className="flex justify-between items-start mb-8">
          {/* Left: Logo and Tagline */}
          <div>
            <img 
              src="/images/demart-logo.jpg" 
              alt="DEMART Logo" 
              className="h-20 w-auto mb-1"
            />
            <div className="text-[10px] font-medium uppercase tracking-wide" style={{ color: '#004aad' }}>
              The Art of Design Engineering Maintenance
            </div>
          </div>
          
          {/* Right: Teklif No and DEMART Yetkilisi */}
          <div className="text-right">
            <div className="bg-blue-600 px-6 py-3 mb-4">
              <div className="text-[10px] font-bold uppercase tracking-widest text-white mb-1">
                {proposal.language === 'english' ? 'QUOTATION NO' : 'TEKLİF NO'}
              </div>
              <div className="text-xl font-black text-white">
                {proposal.teklif_no}
              </div>
            </div>
            
            {/* DEMART Yetkilisi - Below Teklif No */}
            {proposal.representative_name && (
              <div className="space-y-1">
                <div className="text-[10px] font-bold uppercase tracking-widest mb-2" style={{ color: '#004aad' }}>
                  {proposal.language === 'english' ? 'YOUR CONTACT' : 'KONTAĞINIZ'}
                </div>
                <div className="text-sm font-semibold" style={{ color: '#004aad' }}>
                  {proposal.representative_name}
                </div>
                <div className="text-sm" style={{ color: '#004aad' }}>
                  {proposal.representative_phone}
                </div>
                <div className="text-sm" style={{ color: '#004aad' }}>
                  {proposal.representative_email}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Second Section - Info Blocks */}
        <div className="grid grid-cols-2 gap-x-16 gap-y-4 mb-8">
          {/* Left Column */}
          <div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">
              {proposal.language === 'english' ? 'DATE' : 'TARIH'}
            </div>
            <div className="text-sm font-semibold text-gray-900">
              {formatDate(proposal.tarih)}
            </div>
          </div>
          
          {/* Right Column */}
          <div>
            <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">
              {proposal.language === 'english' ? 'CUSTOMER INFORMATION' : 'MÜŞTERİ BİLGİLERİ'}
            </div>
            <div className="text-sm font-semibold text-gray-900">
              {proposal.musteri_firma_adi}
            </div>
          </div>
        </div>

        {/* Main Title Section */}
        <div className="flex-1 flex flex-col justify-center">
          <div className="bg-blue-600 inline-block px-4 py-2 mb-6 self-start">
            <div className="text-xs font-bold uppercase tracking-widest text-white">
              {proposal.language === 'english' ? 'TECHNICAL EVALUATION AND QUOTATION DOCUMENT' : 'TEKNİK DEĞERLENDİRME VE TEKLİF DOSYASI'}
            </div>
          </div>
          <div className="border-l-4 border-blue-600 pl-6">
            <h1 className="text-3xl font-black text-gray-900 uppercase leading-tight">
              {proposal.proje_basligi}
            </h1>
          </div>
        </div>

        {/* Bottom Section - Company Info */}
        <div className="mt-auto pt-6 border-t border-gray-300">
          <div className="flex justify-between items-end">
            <div>
              <div className="text-sm font-bold text-gray-900 mb-2">
                DEMART MÜHENDİSLİK SAN. TİC. LTD. ŞTİ.
              </div>
              <div className="text-xs text-gray-800 mb-1 italic">
                {proposal.language === 'english' 
                  ? 'Protect Safety, Efficiency, and the Future Together'
                  : 'Güvenliği, Verimliliği ve Geleceği Bir Arada Koruyun'}
              </div>
              <div className="text-xs text-gray-700 space-y-0.5">
                <div className="text-blue-600 font-medium">
                  www.demart.com.tr  info@demart.com.tr
                </div>
                <div>VeliBaba Mah. Ertuğrul Gazi Cad. No 82/1</div>
                <div>
                  35852 Pendik İstanbul {proposal.language === 'english' ? 'TURKEY' : 'TÜRKİYE'}
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <img 
                src="/images/sofis-logo.jpeg" 
                alt="Sofis Logo" 
                className="h-20 w-auto ml-auto mb-1"
              />
              <div className="text-xs text-gray-700 font-medium">
                Official Distributor
              </div>
              <div className="text-xs text-gray-700">
                Turkey • Azerbaijan
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProposalCover;